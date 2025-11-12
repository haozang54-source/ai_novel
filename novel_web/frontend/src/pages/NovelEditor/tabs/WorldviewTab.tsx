import { useEffect, useState } from 'react';
import { Card, Button, Tree, Drawer, Form, Input, Select, message, Space, InputNumber, Collapse } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { worldviewApi } from '../../../services/api';
import type { Worldview } from '../../../types';
import type { DataNode } from 'antd/es/tree';

const { TextArea } = Input;
const { Panel } = Collapse;

interface WorldviewTabProps {
  projectId: number;
}

export default function WorldviewTab({ projectId }: WorldviewTabProps) {
  const [worldviews, setWorldviews] = useState<Worldview[]>([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Worldview | null>(null);
  const [form] = Form.useForm();

  const fetchWorldviews = async () => {
    setLoading(true);
    try {
      const response = await worldviewApi.list(projectId);
      setWorldviews(response.data);
    } catch (error) {
      message.error('获取世界观失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorldviews();
  }, [projectId]);

  const convertToTreeData = (items: Worldview[]): DataNode[] => {
    return items.map(item => ({
      key: item.id,
      title: `${item.title || item.name} (${item.category})`,
      children: item.children ? convertToTreeData(item.children) : [],
    }));
  };

  const handleCreate = () => {
    form.resetFields();
    setEditingItem(null);
    setDrawerOpen(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      const data = {
        ...values,
        project_id: projectId,
        tags: values.tags || [],
      };

      if (editingItem) {
        await worldviewApi.update(editingItem.id, data);
        message.success('更新成功');
      } else {
        await worldviewApi.create(data);
        message.success('创建成功');
      }
      
      setDrawerOpen(false);
      fetchWorldviews();
    } catch (error) {
      message.error('保存失败');
    }
  };

  return (
    <div>
      <Card
        title="世界观设定"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            添加设定
          </Button>
        }
      >
        {worldviews.length > 0 ? (
          <Tree
            treeData={convertToTreeData(worldviews)}
            defaultExpandAll
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
            暂无世界观设定，点击"添加设定"开始创建
          </div>
        )}
      </Card>

      <Drawer
        title={editingItem ? '编辑设定' : '创建设定'}
        width={720}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          {/* 基本信息 */}
          <Collapse defaultActiveKey={['basic']} style={{ marginBottom: 16 }}>
            <Panel header="基本信息" key="basic">
              <Form.Item name="category" label="分类" rules={[{ required: true }]}>
                <Select mode="multiple" placeholder="可多选">
                  <Select.Option value="力量体系">力量体系</Select.Option>
                  <Select.Option value="社会结构">社会结构</Select.Option>
                  <Select.Option value="历史背景">历史背景</Select.Option>
                  <Select.Option value="文化习俗">文化习俗</Select.Option>
                  <Select.Option value="规则设定">规则设定</Select.Option>
                  <Select.Option value="天地法则">天地法则</Select.Option>
                  <Select.Option value="宗门势力">宗门势力</Select.Option>
                </Select>
              </Form.Item>
              
              <Form.Item name="name" label="名称" rules={[{ required: true }]}>
                <Input placeholder="例如：筑基境界" />
              </Form.Item>
              
              <Form.Item name="title" label="显示标题">
                <Input placeholder="可选，用于展示" />
              </Form.Item>
              
              <Form.Item name="description" label="描述">
                <TextArea rows={4} placeholder="详细描述该设定" />
              </Form.Item>
            </Panel>
          </Collapse>

          {/* 详细属性 */}
          <Collapse style={{ marginBottom: 16 }}>
            <Panel header="详细属性（可选）" key="details">
              <Form.Item name="element_type" label="元素类型">
                <Select mode="multiple" placeholder="可多选">
                  <Select.Option value="修为境界">修为境界</Select.Option>
                  <Select.Option value="功法">功法</Select.Option>
                  <Select.Option value="术法">术法</Select.Option>
                  <Select.Option value="宗门">宗门</Select.Option>
                  <Select.Option value="制度">制度</Select.Option>
                  <Select.Option value="法宝">法宝</Select.Option>
                  <Select.Option value="种族">种族</Select.Option>
                  <Select.Option value="天道">天道</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="power_level" label="力量等级/位阶">
                <Input placeholder="例如：金丹期、地阶上品" />
              </Form.Item>

              <Form.Item name="scope" label="影响范围">
                <Select mode="multiple">
                  <Select.Option value="个人">个人</Select.Option>
                  <Select.Option value="家族">家族</Select.Option>
                  <Select.Option value="宗门">宗门</Select.Option>
                  <Select.Option value="地域">地域</Select.Option>
                  <Select.Option value="天下">天下</Select.Option>
                  <Select.Option value="诸天万界">诸天万界</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="rules" label="运作规则/限制条件">
                <TextArea rows={3} placeholder="描述该设定的运作机制和限制" />
              </Form.Item>

              <Form.Item name="conflicts" label="相关冲突/对立面">
                <TextArea rows={2} placeholder="与哪些设定存在冲突或对立" />
              </Form.Item>

              <Form.Item name="evolution" label="演变历程/发展脉络">
                <TextArea rows={2} placeholder="该设定如何形成和发展" />
              </Form.Item>
            </Panel>
          </Collapse>

          {/* 元数据 */}
          <Collapse style={{ marginBottom: 16 }}>
            <Panel header="元数据" key="meta">
              <Form.Item name="importance" label="重要程度" initialValue={3}>
                <Select>
                  <Select.Option value={1}>★ 次要</Select.Option>
                  <Select.Option value={2}>★★ 一般</Select.Option>
                  <Select.Option value={3}>★★★ 重要</Select.Option>
                  <Select.Option value={4}>★★★★ 核心</Select.Option>
                  <Select.Option value={5}>★★★★★ 关键</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="ai_weight" label="AI参考权重" initialValue={1.0}>
                <Select>
                  <Select.Option value={0.3}>0.3 (极低)</Select.Option>
                  <Select.Option value={0.5}>0.5 (低)</Select.Option>
                  <Select.Option value={1.0}>1.0 (中)</Select.Option>
                  <Select.Option value={1.5}>1.5 (高)</Select.Option>
                  <Select.Option value={2.0}>2.0 (极高)</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="tags" label="标签">
                <Select mode="tags" placeholder="输入后按回车添加标签" />
              </Form.Item>

              <Form.Item name="first_mentioned_chapter" label="首次提及章节">
                <InputNumber min={1} placeholder="章节号" style={{ width: '100%' }} />
              </Form.Item>
            </Panel>
          </Collapse>

          <Button type="primary" htmlType="submit" block size="large">
            保存
          </Button>
        </Form>
      </Drawer>
    </div>
  );
}
