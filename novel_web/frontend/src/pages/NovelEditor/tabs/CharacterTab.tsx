import { useEffect, useState } from 'react';
import { Card, Button, Space, List, Avatar, Tag, Drawer, Form, Input, Select, message } from 'antd';
import { UserOutlined, PlusOutlined } from '@ant-design/icons';
import { characterApi } from '../../../services/api';
import type { Character } from '../../../types';

const { TextArea } = Input;

interface CharacterTabProps {
  projectId: number;
}

export default function CharacterTab({ projectId }: CharacterTabProps) {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null);
  const [form] = Form.useForm();

  const fetchCharacters = async () => {
    setLoading(true);
    try {
      const response = await characterApi.list(projectId);
      setCharacters(response.data);
    } catch (error) {
      message.error('获取人物列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCharacters();
  }, [projectId]);

  const handleCreate = () => {
    form.resetFields();
    setEditingCharacter(null);
    setDrawerOpen(true);
  };

  const handleEdit = (character: Character) => {
    setEditingCharacter(character);
    form.setFieldsValue(character);
    setDrawerOpen(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      const data = {
        ...values,
        project_id: projectId,
        alias: values.alias ? values.alias.split(',').map((s: string) => s.trim()) : [],
        abilities: values.abilities ? values.abilities.split(',').map((s: string) => s.trim()) : [],
        tags: values.tags ? values.tags.split(',').map((s: string) => s.trim()) : [],
      };

      if (editingCharacter) {
        await characterApi.update(editingCharacter.id, data);
        message.success('人物更新成功');
      } else {
        await characterApi.create(data);
        message.success('人物创建成功');
      }
      
      setDrawerOpen(false);
      fetchCharacters();
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await characterApi.delete(id);
      message.success('删除成功');
      fetchCharacters();
    } catch (error) {
      message.error('删除失败');
    }
  };

  return (
    <div>
      <Card
        title="人物管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            添加人物
          </Button>
        }
      >
        <List
          loading={loading}
          dataSource={characters}
          renderItem={(character) => (
            <List.Item
              actions={[
                <Button type="link" onClick={() => handleEdit(character)}>编辑</Button>,
                <Button type="link" danger onClick={() => handleDelete(character.id)}>删除</Button>,
              ]}
            >
              <List.Item.Meta
                avatar={<Avatar icon={<UserOutlined />} src={character.avatar_url} />}
                title={
                  <Space>
                    {character.name}
                    {character.role_type && <Tag>{character.role_type}</Tag>}
                    <Tag color="gold">{'★'.repeat(character.importance)}</Tag>
                  </Space>
                }
                description={
                  <div>
                    <div>{character.personality}</div>
                    {character.tags.length > 0 && (
                      <Space style={{ marginTop: 8 }}>
                        {character.tags.map((tag, idx) => (
                          <Tag key={idx} color="blue">{tag}</Tag>
                        ))}
                      </Space>
                    )}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      <Drawer
        title={editingCharacter ? '编辑人物' : '创建人物'}
        width={640}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="name" label="姓名" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="alias" label="别名">
            <Input placeholder="多个别名用逗号分隔" />
          </Form.Item>
          <Form.Item name="role_type" label="角色类型">
            <Select>
              <Select.Option value="主角">主角</Select.Option>
              <Select.Option value="配角">配角</Select.Option>
              <Select.Option value="反派">反派</Select.Option>
              <Select.Option value="路人">路人</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="gender" label="性别">
            <Select>
              <Select.Option value="男">男</Select.Option>
              <Select.Option value="女">女</Select.Option>
              <Select.Option value="其他">其他</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="age" label="年龄">
            <Input />
          </Form.Item>
          <Form.Item name="appearance" label="外貌描写">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="personality" label="性格特征">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="background" label="背景故事">
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item name="abilities" label="能力">
            <Input placeholder="多个能力用逗号分隔" />
          </Form.Item>
          <Form.Item name="goals" label="人物目标">
            <TextArea rows={2} />
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
          <Form.Item name="tags" label="标签">
            <Input placeholder="多个标签用逗号分隔" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>保存</Button>
        </Form>
      </Drawer>
    </div>
  );
}
