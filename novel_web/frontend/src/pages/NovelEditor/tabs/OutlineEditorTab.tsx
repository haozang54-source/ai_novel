import { useEffect, useState, useRef } from 'react';
import { Button, Space, Drawer, Form, Input, message, Card, Modal, Popconfirm } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useOutlineStore } from '../../../store/outlineStore';
import OutlineCard from '../../../components/OutlineCard';
import axios from 'axios';

const { TextArea } = Input;

interface OutlineEditorTabProps {
  projectId: number;
}

/**
 * 大纲编辑Tab - 专注于大纲结构设计
 */
export default function OutlineEditorTab({ projectId }: OutlineEditorTabProps) {
  const { 
    outline, 
    fetchOutline, 
    generateOutline, 
    isGenerating,
    selectedChapter,
    selectChapter,
    updateChapter
  } = useOutlineStore();
  
  const [isGenerateDrawerOpen, setIsGenerateDrawerOpen] = useState(false);
  const [isEditDrawerOpen, setIsEditDrawerOpen] = useState(false);
  const [isAddChapterModalOpen, setIsAddChapterModalOpen] = useState(false);
  const [isAddVolumeModalOpen, setIsAddVolumeModalOpen] = useState(false);
  const [currentParentId, setCurrentParentId] = useState<number | null>(null);
  const [form] = Form.useForm();
  const [addChapterForm] = Form.useForm();
  const [addVolumeForm] = Form.useForm();
  const hasLoadedRef = useRef(false);
  const loadedProjectIdRef = useRef<number | null>(null);

  useEffect(() => {
    // 防止 React StrictMode 导致的重复调用
    if (hasLoadedRef.current && loadedProjectIdRef.current === projectId) {
      return;
    }
    
    hasLoadedRef.current = true;
    loadedProjectIdRef.current = projectId;
    fetchOutline(projectId);
  }, [projectId, fetchOutline]);

  const handleGenerate = async (values: any) => {
    const outlineLevel = values.outline_level || 'volume';
    const config: any = {
      outline_level: outlineLevel,
      target_volumes: values.target_volumes || 4,
      target_chapters: values.target_chapters || 30,
    };

    if (outlineLevel === 'volume' && values.volume_structure) {
      config.volume_structure = values.volume_structure;
    }

    setIsGenerateDrawerOpen(false);
    message.loading({ content: '正在生成大纲...', key: 'generate', duration: 0 });
    
    try {
      await generateOutline(projectId, config);
      message.success({ content: '大纲生成成功！', key: 'generate' });
    } catch (error) {
      message.error({ content: '大纲生成失败', key: 'generate' });
    }
  };

  const handleEditChapter = async (values: any) => {
    if (selectedChapter) {
      try {
        await updateChapter(selectedChapter.id, values);
        message.success('保存成功');
        setIsEditDrawerOpen(false);
        selectChapter(null);
      } catch (error) {
        message.error('保存失败');
      }
    }
  };

  const handleAddChildChapter = (parentId: number) => {
    setCurrentParentId(parentId);
    addChapterForm.resetFields();
    setIsAddChapterModalOpen(true);
  };

  const handleSubmitNewChapter = async (values: any) => {
    if (!outline || !currentParentId) return;

    try {
      // 获取当前卷的信息
      const parent = outline.chapters.find(ch => ch.id === currentParentId);
      if (!parent) {
        message.error('找不到父卷');
        return;
      }

      // 计算新章节的序号
      const siblings = parent.children || [];
      const maxChapterNum = siblings.length > 0 
        ? Math.max(...siblings.map(ch => ch.chapter_num))
        : 0;

      const newChapterData = {
        outline_id: outline.id,
        parent_id: currentParentId,
        chapter_num: maxChapterNum + 1,
        title: values.title,
        summary: values.summary || '',
        conflicts: values.conflicts || '',
        emotional_beat: values.emotional_beat || '',
        positioning: values.positioning || '',
        key_events: [],
        core_tasks: [],
        key_turns: [],
        outline_type: 'chapter',
        review_status: 'pending',
        order_index: siblings.length
      };

      await axios.post(
        `/api/outline-chapters/${currentParentId}/add-child`,
        newChapterData
      );

      message.success('章节添加成功');
      setIsAddChapterModalOpen(false);
      setCurrentParentId(null);
      
      // 重新获取大纲数据（带层级结构）
      await fetchOutline(projectId);
    } catch (error) {
      console.error('添加章节失败:', error);
      message.error('添加章节失败');
    }
  };

  const handleAddVolume = () => {
    addVolumeForm.resetFields();
    setIsAddVolumeModalOpen(true);
  };

  const handleSubmitNewVolume = async (values: any) => {
    if (!outline) return;

    try {
      // 计算新卷的序号
      const maxVolumeNum = outline.chapters.length > 0 
        ? Math.max(...outline.chapters.map(v => v.chapter_num))
        : 0;

      const newVolumeData = {
        outline_id: outline.id,
        parent_id: null,
        chapter_num: maxVolumeNum + 1,
        title: values.title,
        summary: values.summary || '',
        conflicts: values.conflicts || '',
        emotional_beat: values.emotional_beat || '',
        positioning: values.positioning || '',
        key_events: [],
        core_tasks: [],
        key_turns: [],
        outline_type: 'volume',
        review_status: 'pending',
        order_index: outline.chapters.length
      };

      await axios.post(`/api/outlines/${outline.id}/chapters`, newVolumeData);

      message.success('卷添加成功');
      setIsAddVolumeModalOpen(false);
      
      // 重新获取大纲数据
      await fetchOutline(projectId);
    } catch (error) {
      console.error('添加卷失败:', error);
      message.error('添加卷失败');
    }
  };

  const handleEditNode = (node: any) => {
    selectChapter(node);
    form.setFieldsValue(node);
    setIsEditDrawerOpen(true);
  };

  const handleDeleteNode = async (node: any) => {
    try {
      await axios.delete(`/api/outline-chapters/${node.id}`);
      message.success('删除成功');
      await fetchOutline(projectId);
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  return (
    <div>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" onClick={() => setIsGenerateDrawerOpen(true)}>
            生成大纲
          </Button>
          <Button>导出大纲</Button>
          {outline?.outline_level === 'volume' && (
            <Button 
              type="default" 
              icon={<PlusOutlined />}
              onClick={handleAddVolume}
            >
              添加大纲（卷）
            </Button>
          )}
        </Space>

        {outline?.chapters.length ? (
          outline.chapters.map(node => (
            <OutlineCard
              key={node.id}
              node={node}
              onEdit={handleEditNode}
              onDelete={handleDeleteNode}
              onAddChild={outline.outline_level === 'volume' ? handleAddChildChapter : undefined}
              isVolume={outline.outline_level === 'volume'}
            />
          ))
        ) : (
          <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
            暂无大纲，请点击"生成大纲"开始创作
          </div>
        )}
      </Card>

      <Drawer
        title="生成大纲"
        open={isGenerateDrawerOpen}
        onClose={() => setIsGenerateDrawerOpen(false)}
        width={400}
      >
        <Form layout="vertical" onFinish={handleGenerate} initialValues={{ outline_level: 'volume', target_volumes: 4 }}>
          <Form.Item label="大纲粒度" name="outline_level">
            <select style={{ width: '100%', padding: '8px' }}>
              <option value="volume">卷级大纲（统领全书）</option>
              <option value="chapter">章节大纲（逐章细纲）</option>
            </select>
          </Form.Item>

          <Form.Item shouldUpdate={(prev, cur) => prev.outline_level !== cur.outline_level}>
            {({ getFieldValue }) => {
              const outlineLevel = getFieldValue('outline_level');
              if (outlineLevel === 'volume') {
                return (
                  <>
                    <Form.Item label="预计卷数" name="target_volumes">
                      <input type="number" min={3} max={20} defaultValue={6} style={{ width: '100%', padding: '8px' }} />
                    </Form.Item>
                    <Form.Item label="卷级结构说明" name="volume_structure">
                      <TextArea rows={4} placeholder="例如：第1卷：起点与埋伏&#10;第2卷：冲突升级" />
                    </Form.Item>
                  </>
                );
              }
              return (
                <Form.Item label="预计章节数" name="target_chapters">
                  <input type="number" min={6} max={80} defaultValue={30} style={{ width: '100%', padding: '8px' }} />
                </Form.Item>
              );
            }}
          </Form.Item>

          <Button type="primary" htmlType="submit" block>开始生成</Button>
        </Form>
      </Drawer>

      <Drawer
        title="编辑大纲节点"
        open={isEditDrawerOpen}
        onClose={() => {
          setIsEditDrawerOpen(false);
          selectChapter(null);
        }}
        width={520}
      >
        <Form form={form} layout="vertical" onFinish={handleEditChapter}>
          <Form.Item name="title" label="节点标题">
            <Input />
          </Form.Item>
          <Form.Item name="summary" label="摘要">
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item name="positioning" label="定位">
            <Input placeholder="该卷/章节在全书中的位置与作用" />
          </Form.Item>
          <Form.Item name="conflicts" label="核心冲突">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="emotional_beat" label="情感基调">
            <Input />
          </Form.Item>
          <Form.Item name="character_growth" label="人物成长">
            <TextArea rows={3} />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>保存</Button>
        </Form>
      </Drawer>

      <Modal
        title="为该卷添加章节"
        open={isAddChapterModalOpen}
        onCancel={() => {
          setIsAddChapterModalOpen(false);
          setCurrentParentId(null);
        }}
        footer={null}
        width={600}
      >
        <Form form={addChapterForm} layout="vertical" onFinish={handleSubmitNewChapter}>
          <Form.Item 
            name="title" 
            label="章节标题" 
            rules={[{ required: true, message: '请输入章节标题' }]}
          >
            <Input placeholder="例如：初入修仙界" />
          </Form.Item>
          <Form.Item 
            name="summary" 
            label="章节摘要"
            rules={[{ required: true, message: '请输入章节摘要' }]}
          >
            <TextArea rows={4} placeholder="简要描述本章节的主要内容" />
          </Form.Item>
          <Form.Item name="positioning" label="定位">
            <Input placeholder="该章节在本卷中的位置与作用" />
          </Form.Item>
          <Form.Item name="conflicts" label="核心冲突">
            <TextArea rows={3} placeholder="本章节的主要冲突或矛盾" />
          </Form.Item>
          <Form.Item name="emotional_beat" label="情感基调">
            <Input placeholder="例如：紧张、激动、悲伤等" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>添加章节</Button>
        </Form>
      </Modal>

      <Modal
        title="添加新卷"
        open={isAddVolumeModalOpen}
        onCancel={() => setIsAddVolumeModalOpen(false)}
        footer={null}
        width={600}
      >
        <Form form={addVolumeForm} layout="vertical" onFinish={handleSubmitNewVolume}>
          <Form.Item 
            name="title" 
            label="卷标题" 
            rules={[{ required: true, message: '请输入卷标题' }]}
          >
            <Input placeholder="例如：第一卷：修仙之路" />
          </Form.Item>
          <Form.Item 
            name="summary" 
            label="卷摘要"
            rules={[{ required: true, message: '请输入卷摘要' }]}
          >
            <TextArea rows={4} placeholder="简要描述本卷的主要内容" />
          </Form.Item>
          <Form.Item name="positioning" label="定位">
            <Input placeholder="该卷在全书中的位置与作用" />
          </Form.Item>
          <Form.Item name="conflicts" label="核心冲突">
            <TextArea rows={3} placeholder="本卷的主要冲突或矛盾" />
          </Form.Item>
          <Form.Item name="emotional_beat" label="情感基调">
            <Input placeholder="例如：紧张、激动、悲伤等" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>添加卷</Button>
        </Form>
      </Modal>
    </div>
  );
}
