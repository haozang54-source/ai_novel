import { useEffect, useState } from 'react';
import { Card, Button, Tree, Drawer, Form, Input, Select, message, Collapse, InputNumber } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { locationApi } from '../../../services/api';
import type { Location } from '../../../types';
import type { DataNode } from 'antd/es/tree';

const { TextArea } = Input;
const { Panel } = Collapse;

interface LocationTabProps {
  projectId: number;
}

export default function LocationTab({ projectId }: LocationTabProps) {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Location | null>(null);
  const [form] = Form.useForm();

  const fetchLocations = async () => {
    setLoading(true);
    try {
      const response = await locationApi.list(projectId);
      setLocations(response.data);
    } catch (error) {
      message.error('获取地点失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocations();
  }, [projectId]);

  const convertToTreeData = (items: Location[]): DataNode[] => {
    return items.map(item => ({
      key: item.id,
      title: `${item.name}${item.location_type ? ` (${item.location_type})` : ''}`,
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
        await locationApi.update(editingItem.id, data);
        message.success('更新成功');
      } else {
        await locationApi.create(data);
        message.success('创建成功');
      }
      
      setDrawerOpen(false);
      fetchLocations();
    } catch (error) {
      message.error('保存失败');
    }
  };

  return (
    <div>
      <Card
        title="地点/地图"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            添加地点
          </Button>
        }
      >
        {locations.length > 0 ? (
          <Tree
            treeData={convertToTreeData(locations)}
            defaultExpandAll
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
            暂无地点设定，点击"添加地点"开始创建
          </div>
        )}
      </Card>

      <Drawer
        title={editingItem ? '编辑地点' : '创建地点'}
        width={720}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          {/* 基本信息 */}
          <Collapse defaultActiveKey={['basic']} style={{ marginBottom: 16 }}>
            <Panel header="基本信息" key="basic">
              <Form.Item name="name" label="地点名称" rules={[{ required: true }]}>
                <Input placeholder="例如：望月湖" />
              </Form.Item>
              
              <Form.Item name="location_type" label="地点类型">
                <Select mode="multiple" placeholder="可多选">
                  <Select.Option value="大陆">大陆</Select.Option>
                  <Select.Option value="国家">国家/王朝</Select.Option>
                  <Select.Option value="城市">城市/城镇</Select.Option>
                  <Select.Option value="村落">村落/聚居地</Select.Option>
                  <Select.Option value="山脉">山脉/山峰</Select.Option>
                  <Select.Option value="湖泊">湖泊/河流</Select.Option>
                  <Select.Option value="建筑">建筑/宫殿</Select.Option>
                  <Select.Option value="房间">房间/密室</Select.Option>
                  <Select.Option value="秘境">秘境/洞府</Select.Option>
                  <Select.Option value="其他">其他</Select.Option>
                </Select>
              </Form.Item>
              
              <Form.Item name="description" label="描述">
                <TextArea rows={4} placeholder="详细描述地点特征" />
              </Form.Item>
            </Panel>
          </Collapse>

          {/* 环境特征 */}
          <Collapse style={{ marginBottom: 16 }}>
            <Panel header="环境特征（可选）" key="environment">
              <Form.Item name="climate" label="气候">
                <Select mode="multiple">
                  <Select.Option value="温和">温和</Select.Option>
                  <Select.Option value="炎热">炎热</Select.Option>
                  <Select.Option value="寒冷">寒冷</Select.Option>
                  <Select.Option value="干燥">干燥</Select.Option>
                  <Select.Option value="潮湿">潮湿</Select.Option>
                  <Select.Option value="多雨">多雨</Select.Option>
                  <Select.Option value="常年积雪">常年积雪</Select.Option>
                  <Select.Option value="灵气充沛">灵气充沛</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="terrain" label="地形">
                <Select mode="multiple">
                  <Select.Option value="平原">平原</Select.Option>
                  <Select.Option value="山地">山地</Select.Option>
                  <Select.Option value="丘陵">丘陵</Select.Option>
                  <Select.Option value="盆地">盆地</Select.Option>
                  <Select.Option value="峡谷">峡谷</Select.Option>
                  <Select.Option value="森林">森林</Select.Option>
                  <Select.Option value="沙漠">沙漠</Select.Option>
                  <Select.Option value="水域">水域</Select.Option>
                  <Select.Option value="悬空">悬空</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="special_features" label="特殊地貌/建筑特点">
                <TextArea rows={3} placeholder="描述独特的景观或建筑特色" />
              </Form.Item>

              <Form.Item name="culture" label="文化特色">
                <TextArea rows={2} placeholder="当地的文化、习俗" />
              </Form.Item>

              <Form.Item name="population" label="人口规模">
                <Select>
                  <Select.Option value="无人">无人</Select.Option>
                  <Select.Option value="稀少">稀少 (&lt;100)</Select.Option>
                  <Select.Option value="小">小 (100-1000)</Select.Option>
                  <Select.Option value="中">中 (1000-10000)</Select.Option>
                  <Select.Option value="大">大 (10000-100000)</Select.Option>
                  <Select.Option value="巨大">巨大 (&gt;100000)</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="government" label="治理/势力">
                <Input placeholder="统治势力或管理方式" />
              </Form.Item>

              <Form.Item name="economy" label="经济/资源">
                <TextArea rows={2} placeholder="主要产业、资源分布" />
              </Form.Item>

              <Form.Item name="history" label="历史背景">
                <TextArea rows={3} placeholder="地点的历史沿革" />
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
