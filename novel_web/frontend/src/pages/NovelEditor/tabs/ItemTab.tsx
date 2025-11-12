import { useEffect, useState } from 'react';
import { Card, Button, List, Tag, Drawer, Form, Input, Select, message, Collapse, InputNumber, Popconfirm } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { itemApi } from '../../../services/api';
import type { Item } from '../../../types';

const { TextArea } = Input;
const { Panel } = Collapse;

interface ItemTabProps {
  projectId: number;
}

export default function ItemTab({ projectId }: ItemTabProps) {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [form] = Form.useForm();

  const fetchItems = async () => {
    setLoading(true);
    try {
      const response = await itemApi.list(projectId);
      setItems(response.data);
    } catch (error) {
      message.error('获取物品失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [projectId]);

  const handleCreate = () => {
    form.resetFields();
    setEditingItem(null);
    setDrawerOpen(true);
  };

  const handleEdit = (item: Item) => {
    setEditingItem(item);
    form.setFieldsValue(item);
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
        await itemApi.update(editingItem.id, data);
        message.success('更新成功');
      } else {
        await itemApi.create(data);
        message.success('创建成功');
      }
      
      setDrawerOpen(false);
      fetchItems();
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await itemApi.delete(id);
      message.success('删除成功');
      fetchItems();
    } catch (error) {
      message.error('删除失败');
    }
  };

  return (
    <div>
      <Card
        title="物品/道具"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            添加物品
          </Button>
        }
      >
        <List
          loading={loading}
          dataSource={items}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Button type="link" onClick={() => handleEdit(item)}>编辑</Button>,
                <Popconfirm
                  title="确定删除此物品吗？"
                  onConfirm={() => handleDelete(item.id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button type="link" danger>删除</Button>
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                title={
                  <>
                    {item.name}
                    {item.category && <Tag style={{ marginLeft: 8 }}>{item.category}</Tag>}
                    {item.level && <Tag color="blue">{item.level}</Tag>}
                    {item.rarity && <Tag color="purple">{item.rarity}</Tag>}
                  </>
                }
                description={item.description}
              />
            </List.Item>
          )}
        />
      </Card>

      <Drawer
        title={editingItem ? '编辑物品' : '创建物品'}
        width={720}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          {/* 基本信息 */}
          <Collapse defaultActiveKey={['basic']} style={{ marginBottom: 16 }}>
            <Panel header="基本信息" key="basic">
              <Form.Item name="name" label="物品名称" rules={[{ required: true }]}>
                <Input placeholder="例如：玄冰剑" />
              </Form.Item>
              
              <Form.Item name="category" label="分类">
                <Select mode="multiple" placeholder="可多选">
                  <Select.Option value="武器">武器</Select.Option>
                  <Select.Option value="法宝">法宝</Select.Option>
                  <Select.Option value="丹药">丹药</Select.Option>
                  <Select.Option value="功法">功法</Select.Option>
                  <Select.Option value="秘籍">秘籍</Select.Option>
                  <Select.Option value="灵材">灵材</Select.Option>
                  <Select.Option value="符箓">符箓</Select.Option>
                  <Select.Option value="宝物">宝物</Select.Option>
                  <Select.Option value="消耗品">消耗品</Select.Option>
                  <Select.Option value="其他">其他</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="description" label="描述">
                <TextArea rows={3} placeholder="简要描述物品" />
              </Form.Item>

              <Form.Item name="appearance" label="外观描写">
                <TextArea rows={2} placeholder="详细描述物品外观" />
              </Form.Item>
            </Panel>
          </Collapse>

          {/* 属性与能力 */}
          <Collapse style={{ marginBottom: 16 }}>
            <Panel header="属性与能力" key="attributes">
              <Form.Item name="level" label="品阶/等级">
                <Select>
                  <Select.Option value="凡品">凡品</Select.Option>
                  <Select.Option value="下品">下品</Select.Option>
                  <Select.Option value="中品">中品</Select.Option>
                  <Select.Option value="上品">上品</Select.Option>
                  <Select.Option value="极品">极品</Select.Option>
                  <Select.Option value="灵器">灵器</Select.Option>
                  <Select.Option value="宝器">宝器</Select.Option>
                  <Select.Option value="神器">神器</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="rarity" label="稀有度">
                <Select mode="multiple">
                  <Select.Option value="普通">普通</Select.Option>
                  <Select.Option value="稀有">稀有</Select.Option>
                  <Select.Option value="罕见">罕见</Select.Option>
                  <Select.Option value="史诗">史诗</Select.Option>
                  <Select.Option value="传说">传说</Select.Option>
                  <Select.Option value="神话">神话</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="abilities" label="功能/能力">
                <TextArea rows={3} placeholder="描述物品的功能和能力" />
              </Form.Item>

              <Form.Item name="effects" label="效果">
                <TextArea rows={2} placeholder="使用效果" />
              </Form.Item>

              <Form.Item name="side_effects" label="副作用">
                <TextArea rows={2} placeholder="负面效果或限制" />
              </Form.Item>

              <Form.Item name="usage_conditions" label="使用条件">
                <TextArea rows={2} placeholder="使用要求、限制" />
              </Form.Item>

              <Form.Item name="durability" label="耐久度">
                <Select>
                  <Select.Option value="一次性">一次性</Select.Option>
                  <Select.Option value="有限">有限</Select.Option>
                  <Select.Option value="普通">普通</Select.Option>
                  <Select.Option value="持久">持久</Select.Option>
                  <Select.Option value="永久">永久</Select.Option>
                  <Select.Option value="不朽">不朽</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="value" label="价值">
                <Input placeholder="例如：100灵石" />
              </Form.Item>
            </Panel>
          </Collapse>

          {/* 来源与历史 */}
          <Collapse style={{ marginBottom: 16 }}>
            <Panel header="来源与历史（可选）" key="history">
              <Form.Item name="origin" label="来历/获得方式">
                <TextArea rows={2} placeholder="物品的出处或获得途径" />
              </Form.Item>

              <Form.Item name="crafting_method" label="炼制方法">
                <TextArea rows={2} placeholder="如何制作或炼制" />
              </Form.Item>

              <Form.Item name="materials" label="材料">
                <TextArea rows={2} placeholder="所需材料或组成" />
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

              <Form.Item name="first_appearance" label="首次出现章节">
                <InputNumber min={1} placeholder="章节号" style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item name="status" label="当前状态" initialValue="normal">
                <Select>
                  <Select.Option value="normal">正常</Select.Option>
                  <Select.Option value="damaged">损坏</Select.Option>
                  <Select.Option value="lost">遗失</Select.Option>
                  <Select.Option value="destroyed">已毁</Select.Option>
                  <Select.Option value="sealed">封印</Select.Option>
                </Select>
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
