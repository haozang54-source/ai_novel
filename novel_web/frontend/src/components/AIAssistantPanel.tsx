import { useState, useEffect } from 'react';
import { 
  Drawer, 
  Input, 
  Button, 
  Select, 
  Space, 
  Divider, 
  Typography, 
  Checkbox, 
  message,
  Spin,
  Card
} from 'antd';
import { 
  RobotOutlined, 
  SendOutlined, 
  RedoOutlined, 
  CheckOutlined,
  CloseOutlined 
} from '@ant-design/icons';
import axios from 'axios';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface KnowledgeBase {
  characters: Array<{ id: number; name: string; role: string }>;
  worldviews: Array<{ id: number; name: string; category: string }>;
  locations: Array<{ id: number; name: string; type: string }>;
  items: Array<{ id: number; name: string; category: string }>;
  foreshadowings: Array<{ id: number; title: string; status: string }>;
  writing_style: any;
}

interface AIAssistantPanelProps {
  visible: boolean;
  onClose: () => void;
  projectId: number;
  selectedText: string;
  contextBefore?: string;
  contextAfter?: string;
  chapterId?: number;
  onApply: (newText: string) => void;
  onCancel: () => void;
}

export default function AIAssistantPanel({
  visible,
  onClose,
  projectId,
  selectedText,
  contextBefore = '',
  contextAfter = '',
  chapterId,
  onApply,
  onCancel
}: AIAssistantPanelProps) {
  const [userPrompt, setUserPrompt] = useState('');
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [selectedKnowledge, setSelectedKnowledge] = useState<{
    character_ids: number[];
    worldview_ids: number[];
    location_ids: number[];
    item_ids: number[];
    foreshadowing_ids: number[];
    writing_style_id?: number;
  }>({
    character_ids: [],
    worldview_ids: [],
    location_ids: [],
    item_ids: [],
    foreshadowing_ids: []
  });
  
  const [aiResponse, setAiResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [editedText, setEditedText] = useState('');
  const [conversationHistory, setConversationHistory] = useState<Array<{
    role: 'user' | 'assistant';
    content: string;
  }>>([]);

  // 加载知识库
  useEffect(() => {
    if (visible && projectId) {
      loadKnowledgeBase();
    }
  }, [visible, projectId]);

  // 当AI返回结果时，更新编辑文本
  useEffect(() => {
    if (aiResponse?.suggested_text) {
      setEditedText(aiResponse.suggested_text);
    }
  }, [aiResponse]);

  const loadKnowledgeBase = async () => {
    try {
      const response = await axios.get(`/api/ai-assistant/knowledge-base/${projectId}`);
      setKnowledgeBase(response.data);
      
      // 如果有文风设定，默认选中
      if (response.data.writing_style) {
        setSelectedKnowledge(prev => ({
          ...prev,
          writing_style_id: response.data.writing_style.id
        }));
      }
    } catch (error) {
      message.error('加载知识库失败');
    }
  };

  const handleAnalyze = async () => {
    if (!userPrompt.trim()) {
      message.warning('请输入修改指令');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/ai-assistant/analyze', {
        project_id: projectId,
        selected_text: selectedText,
        user_prompt: userPrompt,
        context: {
          chapter_id: chapterId,
          before_text: contextBefore,
          after_text: contextAfter
        },
        knowledge_base: selectedKnowledge
      });

      setAiResponse(response.data);
      
      // 添加到对话历史
      setConversationHistory([
        ...conversationHistory,
        { role: 'user', content: userPrompt },
        { role: 'assistant', content: response.data.explanation }
      ]);
      
      message.success('AI分析完成');
    } catch (error) {
      message.error('AI分析失败');
    } finally {
      setLoading(false);
    }
  };

  const handleContinueChat = () => {
    // 继续对话，保留当前AI结果，允许用户继续提问
    setUserPrompt('');
  };

  const handleApply = () => {
    onApply(editedText);
    handleReset();
    onClose();
    // 移除这里的提示，让调用方决定提示内容
  };

  const handleCancelEdit = () => {
    onCancel();
    handleReset();
    onClose();
  };

  const handleReset = () => {
    setUserPrompt('');
    setAiResponse(null);
    setEditedText('');
    setConversationHistory([]);
    setSelectedKnowledge({
      character_ids: [],
      worldview_ids: [],
      location_ids: [],
      item_ids: [],
      foreshadowing_ids: [],
      writing_style_id: knowledgeBase?.writing_style?.id
    });
  };

  return (
    <Drawer
      title={
        <Space>
          <RobotOutlined />
          <span>AI写作助手</span>
        </Space>
      }
      placement="right"
      width={600}
      open={visible}
      onClose={() => {
        handleReset();
        onClose();
      }}
      footer={
        aiResponse && (
          <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
            <Button icon={<CloseOutlined />} onClick={handleCancelEdit}>
              取消
            </Button>
            <Button icon={<RedoOutlined />} onClick={handleReset}>
              重置
            </Button>
            <Button 
              type="primary" 
              icon={<CheckOutlined />} 
              onClick={handleApply}
            >
              应用修改
            </Button>
          </Space>
        )
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 选中的文本 */}
        <Card size="small" title="选中文本">
          <Paragraph style={{ 
            background: '#f5f5f5', 
            padding: '12px', 
            borderRadius: '4px',
            maxHeight: '150px',
            overflow: 'auto'
          }}>
            {selectedText || '未选择文本'}
          </Paragraph>
        </Card>

        {/* 知识库选择 */}
        <div>
          <Title level={5}>选择知识库</Title>
          <Space direction="vertical" style={{ width: '100%' }}>
            {knowledgeBase && (
              <>
                <Select
                  mode="multiple"
                  placeholder="选择相关人物"
                  style={{ width: '100%' }}
                  value={selectedKnowledge.character_ids}
                  onChange={(value) => setSelectedKnowledge({ ...selectedKnowledge, character_ids: value })}
                >
                  {knowledgeBase.characters.map(c => (
                    <Option key={c.id} value={c.id}>
                      {c.name} ({c.role})
                    </Option>
                  ))}
                </Select>

                <Select
                  mode="multiple"
                  placeholder="选择世界观设定"
                  style={{ width: '100%' }}
                  value={selectedKnowledge.worldview_ids}
                  onChange={(value) => setSelectedKnowledge({ ...selectedKnowledge, worldview_ids: value })}
                >
                  {knowledgeBase.worldviews.map(w => (
                    <Option key={w.id} value={w.id}>
                      {w.name} ({w.category})
                    </Option>
                  ))}
                </Select>

                <Select
                  mode="multiple"
                  placeholder="选择地点"
                  style={{ width: '100%' }}
                  value={selectedKnowledge.location_ids}
                  onChange={(value) => setSelectedKnowledge({ ...selectedKnowledge, location_ids: value })}
                >
                  {knowledgeBase.locations.map(l => (
                    <Option key={l.id} value={l.id}>
                      {l.name} ({l.type})
                    </Option>
                  ))}
                </Select>

                <Select
                  mode="multiple"
                  placeholder="选择物品/道具"
                  style={{ width: '100%' }}
                  value={selectedKnowledge.item_ids}
                  onChange={(value) => setSelectedKnowledge({ ...selectedKnowledge, item_ids: value })}
                >
                  {knowledgeBase.items.map(i => (
                    <Option key={i.id} value={i.id}>
                      {i.name} ({i.category})
                    </Option>
                  ))}
                </Select>

                <Select
                  mode="multiple"
                  placeholder="选择伏笔"
                  style={{ width: '100%' }}
                  value={selectedKnowledge.foreshadowing_ids}
                  onChange={(value) => setSelectedKnowledge({ ...selectedKnowledge, foreshadowing_ids: value })}
                >
                  {knowledgeBase.foreshadowings.map(f => (
                    <Option key={f.id} value={f.id}>
                      {f.title} [{f.status}]
                    </Option>
                  ))}
                </Select>

                {knowledgeBase.writing_style && (
                  <Checkbox
                    checked={selectedKnowledge.writing_style_id === knowledgeBase.writing_style.id}
                    onChange={(e) => setSelectedKnowledge({
                      ...selectedKnowledge,
                      writing_style_id: e.target.checked ? knowledgeBase.writing_style.id : undefined
                    })}
                  >
                    使用项目文风设定
                  </Checkbox>
                )}
              </>
            )}
          </Space>
        </div>

        <Divider />

        {/* 用户指令输入 */}
        <div>
          <Title level={5}>修改指令</Title>
          <TextArea
            rows={4}
            placeholder="告诉AI你想如何修改这段文字，例如：&#10;- 增加更多细节描写&#10;- 改为第一人称视角&#10;- 加入悬疑氛围&#10;- 补充人物心理活动"
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleAnalyze}
            loading={loading}
            style={{ marginTop: 12, width: '100%' }}
          >
            AI分析
          </Button>
        </div>

        {/* 对话历史 */}
        {conversationHistory.length > 0 && (
          <div>
            <Title level={5}>对话历史</Title>
            <div style={{ maxHeight: '200px', overflow: 'auto' }}>
              {conversationHistory.map((msg, idx) => (
                <div key={idx} style={{ 
                  marginBottom: 8,
                  padding: 8,
                  background: msg.role === 'user' ? '#e6f7ff' : '#f0f0f0',
                  borderRadius: 4
                }}>
                  <Text strong>{msg.role === 'user' ? '你' : 'AI'}：</Text>
                  <Text>{msg.content}</Text>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI建议 */}
        {aiResponse && (
          <>
            <Divider />
            <div>
              <Title level={5}>AI建议</Title>
              <Card size="small">
                <Paragraph>{aiResponse.explanation}</Paragraph>
              </Card>
            </div>

            {/* 可编辑的预览文本 */}
            <div>
              <Title level={5}>预览文本（可编辑）</Title>
              <TextArea
                rows={10}
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                style={{ fontFamily: 'monospace' }}
              />
              <Space style={{ marginTop: 12, width: '100%', justifyContent: 'space-between' }}>
                <Text type="secondary">
                  置信度: {(aiResponse.confidence * 100).toFixed(0)}%
                </Text>
                <Button onClick={handleContinueChat}>
                  继续对话
                </Button>
              </Space>
            </div>
          </>
        )}
      </Space>
    </Drawer>
  );
}
