import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Layout, Menu, Typography } from 'antd';
import {
  FileTextOutlined,
  BookOutlined,
  UserOutlined,
  EnvironmentOutlined,
  GoldOutlined,
  BulbOutlined,
  BarChartOutlined,
  GlobalOutlined,
  FontSizeOutlined,
} from '@ant-design/icons';
import { useProjectStore } from '../../store/projectStore';
import GlobalAIAssistant from '../../components/GlobalAIAssistant';
import OutlineEditorTab from './tabs/OutlineEditorTab';
import ChapterWritingTab from './tabs/ChapterWritingTab';
import CharacterTab from './tabs/CharacterTab';
import WorldviewTab from './tabs/WorldviewTab';
import LocationTab from './tabs/LocationTab';
import ItemTab from './tabs/ItemTab';
import ForeshadowingTab from './tabs/ForeshadowingTab';
import WritingStyleTab from './tabs/WritingStyleTab';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

type TabKey = 'outline' | 'chapters' | 'characters' | 'worldview' | 'locations' | 'items' | 'foreshadowing' | 'writingStyle';

export default function NovelEditor() {
  const { id } = useParams<{ id: string }>();
  const projectId = parseInt(id!);
  
  const { currentProject, selectProject } = useProjectStore();
  const [activeTab, setActiveTab] = useState<TabKey>('outline');

  useEffect(() => {
    selectProject(projectId);
  }, [projectId, selectProject]);

  const menuItems = [
    {
      key: 'content',
      label: '故事结构',
      type: 'group',
      children: [
        { key: 'outline', icon: <BookOutlined />, label: '大纲编辑' },
        { key: 'chapters', icon: <FileTextOutlined />, label: '章节编写' },
      ],
    },
    {
      key: 'settings',
      label: '创作设定',
      type: 'group',
      children: [
        { key: 'writingStyle', icon: <FontSizeOutlined />, label: '文风设定' },
        { key: 'worldview', icon: <GlobalOutlined />, label: '世界观' },
        { key: 'characters', icon: <UserOutlined />, label: '人物' },
        { key: 'locations', icon: <EnvironmentOutlined />, label: '地点/地图' },
        { key: 'items', icon: <GoldOutlined />, label: '物品/道具' },
      ],
    },
    {
      key: 'tools',
      label: '创作辅助',
      type: 'group',
      children: [
        { key: 'foreshadowing', icon: <BulbOutlined />, label: '伏笔管理' },
      ],
    },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'outline':
        return <OutlineEditorTab projectId={projectId} />;
      case 'chapters':
        return <ChapterWritingTab projectId={projectId} />;
      case 'characters':
        return <CharacterTab projectId={projectId} />;
      case 'worldview':
        return <WorldviewTab projectId={projectId} />;
      case 'locations':
        return <LocationTab projectId={projectId} />;
      case 'items':
        return <ItemTab projectId={projectId} />;
      case 'foreshadowing':
        return <ForeshadowingTab projectId={projectId} />;
      case 'writingStyle':
        return <WritingStyleTab projectId={projectId} />;
      default:
        return <OutlineEditorTab projectId={projectId} />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
        <Title level={3} style={{ margin: '16px 0' }}>
          {currentProject?.title || '小说编辑器'}
        </Title>
      </Header>
      
      <Layout>
        <Sider width={220} style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
          <Menu
            mode="inline"
            selectedKeys={[activeTab]}
            onClick={({ key }) => setActiveTab(key as TabKey)}
            items={menuItems}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>
        
        <Content style={{ padding: '24px', background: '#f5f5f5', minHeight: 280 }}>
          {renderContent()}
        </Content>
      </Layout>

      {/* 全局AI助手 */}
      <GlobalAIAssistant projectId={projectId} enabled={true} />
    </Layout>
  );
}
