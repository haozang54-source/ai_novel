import { useEffect, useState, useRef } from 'react';
import { 
  Card, 
  Button, 
  Space, 
  Typography, 
  Input, 
  message, 
  Spin,
  Tag,
  Divider,
  Row,
  Col,
  Modal,
  Form,
  Popconfirm,
  Tree,
  List
} from 'antd';
import { 
  EditOutlined, 
  SaveOutlined,
  FileTextOutlined,
  PlusOutlined,
  DeleteOutlined,
  FolderOutlined,
  FileOutlined
} from '@ant-design/icons';
import type { TreeDataNode } from 'antd';
import axios from 'axios';
import { chapterApi } from '../../../services/api';
import { useOutlineStore } from '../../../store/outlineStore';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface Chapter {
  id?: number;
  outline_chapter_id: number;
  content: string;
  word_count: number;
  status: string;
}

interface ChapterInfo {
  outline_chapter_id: number;
  chapter_num: number;
  title: string;
  summary: string;
  parent_id?: number;
  chapter: Chapter | null;
}

interface ProjectChaptersResponse {
  message: string;
  outline_level: 'chapter' | 'volume' | null;
  chapters: ChapterInfo[];
  volumes?: Array<{
    outline_chapter_id: number;
    volume_num: number;
    title: string;
    summary: string;
  }>;
}

interface VolumeNode {
  id: number;
  outline_chapter_id: number;
  volume_num: number;
  title: string;
  summary: string;
  children: ChapterInfo[];
}

// Tree节点的Key类型
type TreeKey = string; // 格式: 'v-{id}' 或 'c-{id}'

interface ChapterWritingTabProps {
  projectId: number;
}

/**
 * 章节编写Tab - 专注于正文创作
 */
export default function ChapterWritingTab({ projectId }: ChapterWritingTabProps) {
  const [chapters, setChapters] = useState<ChapterInfo[]>([]);
  const [volumes, setVolumes] = useState<VolumeNode[]>([]);
  const [outlineLevel, setOutlineLevel] = useState<'chapter' | 'volume' | null>(null);
  
  // 选中状态
  const [selectedKeys, setSelectedKeys] = useState<TreeKey[]>([]);
  const [selectedType, setSelectedType] = useState<'volume' | 'chapter' | null>(null);
  const [selectedVolume, setSelectedVolume] = useState<VolumeNode | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<ChapterInfo | null>(null);
  
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  
  const hasLoadedRef = useRef(false);
  const loadedProjectIdRef = useRef<number | null>(null);
  
  // 章节管理相关状态
  const [isAddModalVisible, setIsAddModalVisible] = useState(false);
  const [isEditChapterModalVisible, setIsEditChapterModalVisible] = useState(false);
  const [editingChapterInfo, setEditingChapterInfo] = useState<ChapterInfo | null>(null);
  const [addForm] = Form.useForm();
  const [editForm] = Form.useForm();
  
  const { outline } = useOutlineStore();

  useEffect(() => {
    // 防止 React StrictMode 导致的重复调用
    if (hasLoadedRef.current && loadedProjectIdRef.current === projectId) {
      return;
    }
    
    hasLoadedRef.current = true;
    loadedProjectIdRef.current = projectId;
    loadChapters();
  }, [projectId]);

  const loadChapters = async () => {
    setLoading(true);
    try {
      const response = await axios.get<ProjectChaptersResponse>(`/api/chapters/project/${projectId}`);
      const data = response.data;
      
      setOutlineLevel(data.outline_level);
      setChapters(data.chapters || []);
      
      // 如果是卷级大纲，构建树形结构
      if (data.outline_level === 'volume') {
        // 获取大纲数据来构建完整的卷结构
        const outlineResponse = await axios.get(`/api/projects/${projectId}/outline?hierarchy=true`);
        const outline = outlineResponse.data;
        
        // 构建卷-章节树
        const volumeNodes: VolumeNode[] = outline.chapters.map((vol: any) => ({
          id: vol.id,
          outline_chapter_id: vol.id,
          volume_num: vol.chapter_num,
          title: vol.title,
          summary: vol.summary,
          children: data.chapters.filter((ch: ChapterInfo) => ch.parent_id === vol.id)
        }));
        
        setVolumes(volumeNodes);
      } else {
        setVolumes([]);
      }
    } catch (error) {
      message.error('加载章节列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理树节点选择
  const handleTreeSelect = (keys: React.Key[]) => {
    if (keys.length === 0) {
      setSelectedKeys([]);
      setSelectedType(null);
      setSelectedVolume(null);
      setSelectedChapter(null);
      setContent('');
      return;
    }
    
    const key = keys[0] as string;
    setSelectedKeys([key]);
    
    // 解析key: 'v-{id}' 或 'c-{id}'
    const [type, idStr] = key.split('-');
    const id = parseInt(idStr);
    
    if (type === 'v') {
      // 选中卷
      const volume = volumes.find(v => v.id === id);
      if (volume) {
        setSelectedType('volume');
        setSelectedVolume(volume);
        setSelectedChapter(null);
        setContent('');
      }
    } else if (type === 'c') {
      // 选中章节
      let chapter: ChapterInfo | undefined;
      
      if (outlineLevel === 'volume') {
        // 卷级大纲：从volumes中查找
        for (const vol of volumes) {
          chapter = vol.children.find(ch => ch.outline_chapter_id === id);
          if (chapter) break;
        }
      } else {
        // 章级大纲：直接从chapters查找
        chapter = chapters.find(ch => ch.outline_chapter_id === id);
      }
      
      if (chapter) {
        setSelectedType('chapter');
        setSelectedVolume(null);
        setSelectedChapter(chapter);
        setContent(chapter.chapter?.content || '');
      }
    }
  };

  const handleSave = async () => {
    if (!selectedChapter) return;

    setSaving(true);
    try {
      await axios.post(`/api/chapters/outline-chapter/${selectedChapter.outline_chapter_id}`, {
        content,
        status: 'draft'
      });
      message.success('保存成功');
      loadChapters();
    } catch (error) {
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      'not_started': { color: 'default', text: '未开始' },
      'draft': { color: 'processing', text: '草稿' },
      'reviewing': { color: 'warning', text: '审阅中' },
      'completed': { color: 'success', text: '已完成' }
    };
    const s = statusMap[status] || statusMap['not_started'];
    return <Tag color={s.color}>{s.text}</Tag>;
  };

  // 新增章节（章级大纲）
  const handleAddChapter = async (values: any) => {
    if (!outline?.id) {
      message.error('未找到大纲信息');
      return;
    }

    try {
      await chapterApi.addOutlineChapter(outline.id, values);
      message.success('章节添加成功');
      setIsAddModalVisible(false);
      addForm.resetFields();
      loadChapters();
    } catch (error) {
      message.error('添加章节失败');
    }
  };

  // 为卷添加子章节（卷级大纲）
  const handleAddChildChapter = async (values: any) => {
    if (!selectedVolume) {
      message.error('请先选择卷');
      return;
    }

    try {
      await axios.post(`/api/outline-chapters/${selectedVolume.id}/add-child`, values);
      message.success('章节添加成功');
      setIsAddModalVisible(false);
      addForm.resetFields();
      loadChapters();
    } catch (error) {
      message.error('添加章节失败');
    }
  };

  // 打开添加章节对话框
  const handleOpenAddModal = () => {
    addForm.resetFields();
    setIsAddModalVisible(true);
  };

  // 编辑章节信息
  const handleEditChapterInfo = (chapterInfo: ChapterInfo) => {
    setEditingChapterInfo(chapterInfo);
    editForm.setFieldsValue({
      title: chapterInfo.title,
      summary: chapterInfo.summary,
    });
    setIsEditChapterModalVisible(true);
  };

  // 保存章节信息编辑
  const handleSaveChapterInfo = async (values: any) => {
    if (!editingChapterInfo) return;

    try {
      await chapterApi.updateOutlineChapter(editingChapterInfo.outline_chapter_id, values);
      message.success('章节信息更新成功');
      setIsEditChapterModalVisible(false);
      setEditingChapterInfo(null);
      editForm.resetFields();
      loadChapters();
    } catch (error) {
      message.error('更新失败');
    }
  };

  // 删除章节
  const handleDeleteChapter = async (outlineChapterId: number) => {
    try {
      await chapterApi.deleteOutlineChapter(outlineChapterId);
      message.success('章节删除成功');
      if (selectedChapter?.outline_chapter_id === outlineChapterId) {
        setSelectedKeys([]);
        setSelectedType(null);
        setSelectedChapter(null);
        setContent('');
      }
      loadChapters();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 构建Tree数据
  const buildTreeData = (): TreeDataNode[] => {
    if (outlineLevel === 'volume') {
      return volumes.map(vol => ({
        key: `v-${vol.id}`,
        title: `第${vol.volume_num}卷：${vol.title}`,
        icon: <FolderOutlined />,
        children: vol.children.map(ch => ({
          key: `c-${ch.outline_chapter_id}`,
          title: `第${ch.chapter_num}章：${ch.title}`,
          icon: <FileOutlined />,
          isLeaf: true
        }))
      }));
    } else {
      return chapters.map(ch => ({
        key: `c-${ch.outline_chapter_id}`,
        title: `第${ch.chapter_num}章：${ch.title}`,
        icon: <FileOutlined />,
        isLeaf: true
      }));
    }
  };

  return (
    <div style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部操作栏 */}
      <Card 
        size="small" 
        style={{ marginBottom: 16 }}
        bodyStyle={{ padding: '8px 16px' }}
      >
        <Space>
          {selectedType === 'volume' && selectedVolume && (
            <>
              <Tag color="blue">已选择：第{selectedVolume.volume_num}卷 {selectedVolume.title}</Tag>
              <Button 
                type="primary" 
                size="small" 
                icon={<PlusOutlined />}
                onClick={handleOpenAddModal}
              >
                添加章节
              </Button>
            </>
          )}
          {selectedType === 'chapter' && selectedChapter && (
            <>
              <Tag color="green">已选择：第{selectedChapter.chapter_num}章 {selectedChapter.title}</Tag>
              <Button
                type="text"
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleEditChapterInfo(selectedChapter)}
              >
                编辑信息
              </Button>
              <Popconfirm
                title="确定删除此章节？"
                description="删除后将无法恢复，包括已编写的正文内容"
                onConfirm={() => handleDeleteChapter(selectedChapter.outline_chapter_id)}
                okText="删除"
                cancelText="取消"
              >
                <Button
                  type="text"
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                >
                  删除章节
                </Button>
              </Popconfirm>
            </>
          )}
          {!selectedType && outlineLevel === 'chapter' && (
            <Button 
              type="primary" 
              size="small" 
              icon={<PlusOutlined />}
              onClick={handleOpenAddModal}
            >
              新增章节
            </Button>
          )}
          {!selectedType && outlineLevel === 'volume' && volumes.length > 0 && (
            <Text type="secondary">💡 请先从左侧选择卷或章节</Text>
          )}
        </Space>
      </Card>

      {/* 主内容区 */}
      <Row gutter={16} style={{ flex: 1, overflow: 'hidden' }}>
        {/* 左侧树形结构 */}
        <Col span={6}>
          <Card 
            title="章节结构"
            style={{ height: '100%' }}
            bodyStyle={{ padding: 12, overflowY: 'auto', height: 'calc(100% - 57px)' }}
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Spin />
              </div>
            ) : (outlineLevel === 'volume' && volumes.length === 0) || (outlineLevel === 'chapter' && chapters.length === 0) ? (
              <div style={{ padding: 24, textAlign: 'center' }}>
                <Text type="secondary">
                  {outlineLevel === 'volume' 
                    ? '暂无卷和章节，请先在"大纲编辑"Tab中生成大纲或添加章节'
                    : '暂无章节，请先在"大纲编辑"Tab中生成大纲'
                  }
                </Text>
              </div>
            ) : (
              <Tree
                showIcon
                selectedKeys={selectedKeys}
                onSelect={handleTreeSelect}
                treeData={buildTreeData()}
                defaultExpandAll
              />
            )}
          </Card>
        </Col>

        {/* 右侧内容区 */}
        <Col span={18}>
          {selectedType === 'chapter' && selectedChapter ? (
            <Card
              title={
                <Space>
                  <FileTextOutlined />
                  <span>第{selectedChapter.chapter_num}章：{selectedChapter.title}</span>
                </Space>
              }
              extra={
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  onClick={handleSave}
                  loading={saving}
                >
                  保存
                </Button>
              }
              style={{ height: '100%' }}
              bodyStyle={{ 
                height: 'calc(100% - 64px)', 
                display: 'flex', 
                flexDirection: 'column',
                overflowY: 'auto'
              }}
            >
              {/* 章节大纲摘要 */}
              <Card 
                size="small" 
                style={{ marginBottom: 16, background: '#fafafa' }}
                title="大纲摘要"
              >
                <Paragraph style={{ margin: 0 }}>
                  {selectedChapter.summary || '暂无大纲'}
                </Paragraph>
              </Card>

              <Divider style={{ margin: '0 0 16px 0' }} />

              {/* 提示信息 */}
              <div style={{ marginBottom: 12 }}>
                <Text type="secondary">
                  💡 选中任意文本后，会自动弹出AI助手按钮进行交互
                </Text>
              </div>

              {/* 文本编辑器 */}
              <TextArea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="开始写作..."
                style={{ 
                  flex: 1,
                  fontFamily: 'serif',
                  fontSize: 16,
                  lineHeight: 1.8,
                  resize: 'none'
                }}
              />

              {/* 统计信息 */}
              <div style={{ marginTop: 12, textAlign: 'right' }}>
                <Space split={<Divider type="vertical" />}>
                  <Text type="secondary">
                    字数: {content.replace(/\s/g, '').length}
                  </Text>
                  <Text type="secondary">
                    段落: {content.split('\n\n').filter(p => p.trim()).length}
                  </Text>
                </Space>
              </div>
            </Card>
          ) : selectedType === 'volume' && selectedVolume ? (
            <Card
              title={
                <Space>
                  <FolderOutlined />
                  <span>第{selectedVolume.volume_num}卷：{selectedVolume.title}</span>
                </Space>
              }
              style={{ height: '100%' }}
              bodyStyle={{ 
                height: 'calc(100% - 64px)', 
                padding: 24,
                overflowY: 'auto'
              }}
            >
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <div>
                  <Title level={5}>卷摘要</Title>
                  <Paragraph>{selectedVolume.summary || '暂无摘要'}</Paragraph>
                </div>
                
                <Divider />
                
                <div>
                  <Title level={5}>包含章节 ({selectedVolume.children.length})</Title>
                  <List
                    dataSource={selectedVolume.children}
                    renderItem={(ch) => (
                      <List.Item
                        actions={[
                          <Button
                            type="link"
                            onClick={() => {
                              setSelectedKeys([`c-${ch.outline_chapter_id}`]);
                              setSelectedType('chapter');
                              setSelectedVolume(null);
                              setSelectedChapter(ch);
                              setContent(ch.chapter?.content || '');
                            }}
                          >
                            编辑正文
                          </Button>
                        ]}
                      >
                        <List.Item.Meta
                          avatar={<FileOutlined />}
                          title={`第${ch.chapter_num}章：${ch.title}`}
                          description={
                            <Space>
                              {getStatusTag(ch.chapter?.status || 'not_started')}
                              {ch.chapter && (
                                <Text type="secondary">{ch.chapter.word_count} 字</Text>
                              )}
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                </div>
              </Space>
            </Card>
          ) : (
            <Card style={{ height: '100%' }}>
              <div style={{ 
                height: '100%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: '#999'
              }}>
                <Space direction="vertical" align="center">
                  <FileTextOutlined style={{ fontSize: 48 }} />
                  <Text type="secondary">请从左侧选择卷或章节</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {outlineLevel === 'volume' 
                      ? '选择卷可以查看卷信息和添加章节，选择章节可以编辑正文'
                      : '选择章节开始编辑正文'
                    }
                  </Text>
                </Space>
              </div>
            </Card>
          )}
        </Col>
      </Row>

      {/* 新增章节模态框 */}
      <Modal
        title={selectedType === 'volume' ? `为"${selectedVolume?.title}"添加章节` : '新增章节'}
        open={isAddModalVisible}
        onCancel={() => {
          setIsAddModalVisible(false);
          addForm.resetFields();
        }}
        onOk={() => addForm.submit()}
        okText="添加"
        cancelText="取消"
      >
        <Form
          form={addForm}
          layout="vertical"
          onFinish={selectedType === 'volume' ? handleAddChildChapter : handleAddChapter}
        >
          <Form.Item
            label="章节标题"
            name="title"
            rules={[{ required: true, message: '请输入章节标题' }]}
          >
            <Input placeholder="例如：初入江湖" />
          </Form.Item>
          <Form.Item
            label="章节摘要"
            name="summary"
          >
            <Input.TextArea 
              rows={4} 
              placeholder="简要描述本章的主要内容、冲突和情节发展..." 
            />
          </Form.Item>
          <Form.Item
            label="核心冲突"
            name="conflicts"
          >
            <Input.TextArea rows={2} placeholder="本章的主要矛盾和冲突..." />
          </Form.Item>
          <Form.Item
            label="情感基调"
            name="emotional_beat"
          >
            <Input placeholder="例如：紧张、激动、悲伤..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑章节信息模态框 */}
      <Modal
        title="编辑章节信息"
        open={isEditChapterModalVisible}
        onCancel={() => {
          setIsEditChapterModalVisible(false);
          setEditingChapterInfo(null);
          editForm.resetFields();
        }}
        onOk={() => editForm.submit()}
        okText="保存"
        cancelText="取消"
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={handleSaveChapterInfo}
        >
          <Form.Item
            label="章节标题"
            name="title"
            rules={[{ required: true, message: '请输入章节标题' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            label="章节摘要"
            name="summary"
          >
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item
            label="核心冲突"
            name="conflicts"
          >
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item
            label="情感基调"
            name="emotional_beat"
          >
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
