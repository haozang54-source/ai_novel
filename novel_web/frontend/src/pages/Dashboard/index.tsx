import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Card, Button, Modal, Form, Input, Select, Row, Col, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useProjectStore } from '../../store/projectStore';

const { Header, Content } = Layout;
const { TextArea } = Input;

export default function Dashboard() {
  const navigate = useNavigate();
  const { projects, fetchProjects, createProject } = useProjectStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (values: any) => {
    const project = await createProject(values);
    setIsModalOpen(false);
    form.resetFields();
    navigate(`/projects/${project.id}`);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h1 style={{ margin: 0 }}>AI小说创作助手</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
          新建项目
        </Button>
      </Header>
      
      <Content style={{ padding: '24px' }}>
        <Row gutter={[16, 16]}>
          {projects.map(project => (
            <Col key={project.id} xs={24} sm={12} lg={8}>
              <Card
                hoverable
                title={project.title}
                extra={<span>{project.genre}</span>}
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                <p>{project.theme}</p>
                <Space>
                  <span>目标: {project.target_length}字</span>
                  <span>状态: {project.status}</span>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      </Content>

      <Modal
        title="新建项目"
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => setIsModalOpen(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateProject}>
          <Form.Item name="title" label="标题" rules={[{ required: true }]}>
            <Input placeholder="输入小说标题" />
          </Form.Item>
          <Form.Item name="genre" label="类型" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="玄幻">玄幻</Select.Option>
              <Select.Option value="仙侠">仙侠</Select.Option>
              <Select.Option value="都市">都市</Select.Option>
              <Select.Option value="科幻">科幻</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="theme" label="主题" rules={[{ required: true }]}>
            <TextArea rows={4} placeholder="描述你的小说创意..." />
          </Form.Item>
          <Form.Item name="target_length" label="目标字数" initialValue={15000}>
            <Input type="number" />
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
}
