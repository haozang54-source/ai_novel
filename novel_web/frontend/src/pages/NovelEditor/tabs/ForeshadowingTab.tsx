import { useEffect, useState } from 'react';
import { Card, Button, Col, Row, List, Tag, Drawer, Form, Input, Select, InputNumber, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { foreshadowingApi } from '../../../services/api';
import type { Foreshadowing } from '../../../types';

const { TextArea } = Input;

interface ForeshadowingTabProps {
  projectId: number;
}

export default function ForeshadowingTab({ projectId }: ForeshadowingTabProps) {
  const [planted, setPlanted] = useState<Foreshadowing[]>([]);
  const [revealed, setRevealed] = useState<Foreshadowing[]>([]);
  const [abandoned, setAbandoned] = useState<Foreshadowing[]>([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Foreshadowing | null>(null);
  const [form] = Form.useForm();

  const fetchForeshadowings = async () => {
    setLoading(true);
    try {
      const response = await foreshadowingApi.list(projectId);
      const data = response.data;
      setPlanted(data.filter((f: Foreshadowing) => f.status === 'planted'));
      setRevealed(data.filter((f: Foreshadowing) => f.status === 'revealed'));
      setAbandoned(data.filter((f: Foreshadowing) => f.status === 'abandoned'));
    } catch (error) {
      message.error('获取伏笔失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForeshadowings();
  }, [projectId]);

  const handleCreate = () => {
    form.resetFields();
    setEditingItem(null);
    setDrawerOpen(true);
  };

  const handleEdit = (item: Foreshadowing) => {
    setEditingItem(item);
    form.setFieldsValue(item);
    setDrawerOpen(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      const data = {
        ...values,
        project_id: projectId,
      };

      if (editingItem) {
        await foreshadowingApi.update(editingItem.id, data);
        message.success('更新成功');
      } else {
        await foreshadowingApi.create(data);
        message.success('创建成功');
      }
      
      setDrawerOpen(false);
      fetchForeshadowings();
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await foreshadowingApi.delete(id);
      message.success('删除成功');
      fetchForeshadowings();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleReveal = async (item: Foreshadowing) => {
    try {
      await foreshadowingApi.update(item.id, {
        status: 'revealed',
        actual_reveal_chapter: item.planned_reveal_chapter,
      });
      message.success('已标记为揭示');
      fetchForeshadowings();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const renderForeshadowingCard = (item: Foreshadowing) => (
    <List.Item
      key={item.id}
      actions={[
        item.status === 'planted' && (
          <Button type="link" size="small" onClick={() => handleReveal(item)}>标记揭示</Button>
        ),
        <Button type="link" size="small" onClick={() => handleEdit(item)}>编辑</Button>,
        <Button type="link" size="small" danger onClick={() => handleDelete(item.id)}>删除</Button>,
      ].filter(Boolean)}
    >
      <List.Item.Meta
        title={
          <>
            {item.title}
            {item.category && <Tag style={{ marginLeft: 8 }}>{item.category}</Tag>}
            <Tag color="gold">重要度: {'★'.repeat(item.importance)}</Tag>
            <Tag color="red">紧迫度: {item.urgency}</Tag>
          </>
        }
        description={
          <div>
            <div>{item.description}</div>
            <div style={{ marginTop: 8, fontSize: '12px', color: '#999' }}>
              埋设章节: {item.planted_chapter || '未设置'} | 
              计划揭晓: {item.planned_reveal_chapter || '未设置'}
              {item.actual_reveal_chapter && ` | 实际揭晓: ${item.actual_reveal_chapter}`}
            </div>
          </div>
        }
      />
    </List.Item>
  );

  return (
    <div>
      <Card
        title="伏笔管理 - 看板视图"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            添加伏笔
          </Button>
        }
      >
        <Row gutter={16}>
          <Col span={8}>
            <Card 
              title="已埋下" 
              size="small" 
              headStyle={{ background: '#e6f7ff', fontWeight: 'bold' }}
            >
              <List
                loading={loading}
                dataSource={planted}
                renderItem={renderForeshadowingCard}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card 
              title="已呼应" 
              size="small"
              headStyle={{ background: '#f6ffed', fontWeight: 'bold' }}
            >
              <List
                loading={loading}
                dataSource={revealed}
                renderItem={renderForeshadowingCard}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card 
              title="已放弃" 
              size="small"
              headStyle={{ background: '#fff1f0', fontWeight: 'bold' }}
            >
              <List
                loading={loading}
                dataSource={abandoned}
                renderItem={renderForeshadowingCard}
              />
            </Card>
          </Col>
        </Row>
      </Card>

      <Drawer
        title={editingItem ? '编辑伏笔' : '创建伏笔'}
        width={640}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="title" label="伏笔标题" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Select>
              <Select.Option value="人物">人物</Select.Option>
              <Select.Option value="剧情">剧情</Select.Option>
              <Select.Option value="物品">物品</Select.Option>
              <Select.Option value="世界观">世界观</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="planted_chapter" label="埋下的章节">
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="planted_content" label="埋设时的具体内容">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="planted_method" label="埋设方式">
            <Select>
              <Select.Option value="明示">明示</Select.Option>
              <Select.Option value="暗示">暗示</Select.Option>
              <Select.Option value="道具">道具</Select.Option>
              <Select.Option value="对话">对话</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="planned_reveal_chapter" label="计划揭晓章节">
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="importance" label="重要程度" initialValue={3}>
            <Select>
              <Select.Option value={1}>★</Select.Option>
              <Select.Option value={2}>★★</Select.Option>
              <Select.Option value={3}>★★★</Select.Option>
              <Select.Option value={4}>★★★★</Select.Option>
              <Select.Option value={5}>★★★★★</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="urgency" label="紧迫度" initialValue={3}>
            <InputNumber min={1} max={5} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="status" label="状态" initialValue="planted">
            <Select>
              <Select.Option value="planted">已埋下</Select.Option>
              <Select.Option value="revealed">已呼应</Select.Option>
              <Select.Option value="abandoned">已放弃</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <TextArea rows={3} />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>保存</Button>
        </Form>
      </Drawer>
    </div>
  );
}
