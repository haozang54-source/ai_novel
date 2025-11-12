import { useEffect, useState } from 'react';
import { Card, Form, Select, Input, Button, message, Space, List } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { writingStyleApi } from '../../../services/api';
import type { WritingStyle } from '../../../types';

const { TextArea } = Input;

interface WritingStyleTabProps {
  projectId: number;
}

export default function WritingStyleTab({ projectId }: WritingStyleTabProps) {
  const [writingStyle, setWritingStyle] = useState<WritingStyle | null>(null);
  const [loading, setLoading] = useState(false);
  const [samples, setSamples] = useState<Array<{ scene_type: string; sample: string }>>([]);
  const [form] = Form.useForm();

  const fetchWritingStyle = async () => {
    setLoading(true);
    try {
      const response = await writingStyleApi.get(projectId);
      if (response.data) {
        setWritingStyle(response.data);
        form.setFieldsValue(response.data);
        setSamples(response.data.style_samples || []);
      }
    } catch (error) {
      message.error('获取文风设定失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWritingStyle();
  }, [projectId]);

  const handleSubmit = async (values: any) => {
    try {
      const data = {
        ...values,
        project_id: projectId,
        style_samples: samples,
      };

      await writingStyleApi.createOrUpdate(projectId, data);
      message.success('保存成功');
      
      fetchWritingStyle();
    } catch (error) {
      message.error('保存失败');
    }
  };

  const addSample = () => {
    setSamples([...samples, { scene_type: '', sample: '' }]);
  };

  const updateSample = (index: number, field: string, value: string) => {
    const newSamples = [...samples];
    newSamples[index] = { ...newSamples[index], [field]: value };
    setSamples(newSamples);
  };

  const removeSample = (index: number) => {
    setSamples(samples.filter((_, i) => i !== index));
  };

  return (
    <div>
      <Card title="文风设定" loading={loading}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="narrative_perspective" label="叙述视角">
            <Select>
              <Select.Option value="第一人称">第一人称</Select.Option>
              <Select.Option value="第三人称全知">第三人称全知</Select.Option>
              <Select.Option value="第三人称限知">第三人称限知</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="language_style" label="语言风格">
            <Select>
              <Select.Option value="现代口语化">现代口语化</Select.Option>
              <Select.Option value="古典文雅">古典文雅</Select.Option>
              <Select.Option value="网文爽文">网文爽文</Select.Option>
              <Select.Option value="诗意抒情">诗意抒情</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="dialogue_style" label="对话风格">
            <Select>
              <Select.Option value="简洁">简洁</Select.Option>
              <Select.Option value="生动">生动</Select.Option>
              <Select.Option value="幽默">幽默</Select.Option>
              <Select.Option value="正式">正式</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="description_density" label="描写密度">
            <Select>
              <Select.Option value="简练">简练</Select.Option>
              <Select.Option value="适中">适中</Select.Option>
              <Select.Option value="细腻">细腻</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="custom_notes" label="其他风格说明">
            <TextArea rows={4} placeholder="描述其他特殊的风格要求..." />
          </Form.Item>

          <Form.Item label="文风样本库">
            <Space direction="vertical" style={{ width: '100%' }}>
              {samples.map((sample, index) => (
                <Card 
                  key={index} 
                  size="small" 
                  title={`样本 ${index + 1}`}
                  extra={
                    <Button 
                      type="link" 
                      danger 
                      icon={<DeleteOutlined />} 
                      onClick={() => removeSample(index)}
                    />
                  }
                >
                  <Input
                    placeholder="场景类型（如：战斗、对话、景物描写）"
                    value={sample.scene_type}
                    onChange={(e) => updateSample(index, 'scene_type', e.target.value)}
                    style={{ marginBottom: 8 }}
                  />
                  <TextArea
                    rows={4}
                    placeholder="样本段落..."
                    value={sample.sample}
                    onChange={(e) => updateSample(index, 'sample', e.target.value)}
                  />
                </Card>
              ))}
              <Button 
                type="dashed" 
                icon={<PlusOutlined />} 
                onClick={addSample}
                block
              >
                添加样本
              </Button>
            </Space>
          </Form.Item>

          <Form.Item name="ai_weight" label="AI参考权重" initialValue={1.0}>
            <Select>
              <Select.Option value={0.5}>0.5 (低)</Select.Option>
              <Select.Option value={1.0}>1.0 (中)</Select.Option>
              <Select.Option value={1.5}>1.5 (高)</Select.Option>
              <Select.Option value={2.0}>2.0 (极高)</Select.Option>
            </Select>
          </Form.Item>

          <Button type="primary" htmlType="submit" block size="large">
            保存文风设定
          </Button>
        </Form>
      </Card>
    </div>
  );
}
