import { useEffect, useState, useRef } from 'react';
import { Button, Space, Drawer, Form, Input, message, Card } from 'antd';
import { useOutlineStore } from '../../../store/outlineStore';
import OutlineCard from '../../../components/OutlineCard';

const { TextArea } = Input;

interface OutlineTabProps {
  projectId: number;
}

export default function OutlineTab({ projectId }: OutlineTabProps) {
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
  const [form] = Form.useForm();
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

  return (
    <div>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" onClick={() => setIsGenerateDrawerOpen(true)}>
            生成大纲
          </Button>
        </Space>

        {outline?.chapters.length ? (
          outline.chapters.map(node => (
            <OutlineCard
              key={node.id}
              node={node}
              onClick={() => {
                selectChapter(node);
                form.setFieldsValue(node);
                setIsEditDrawerOpen(true);
              }}
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
        title="编辑节点"
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
    </div>
  );
}
