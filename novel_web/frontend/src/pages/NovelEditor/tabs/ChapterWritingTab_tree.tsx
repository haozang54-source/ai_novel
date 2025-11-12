// 这是修改后的章节列表渲染逻辑，请将此代码替换到 ChapterWritingTab.tsx 的对应位置

// 1. 在文件顶部的 interface 中添加：
interface VolumeTreeNode {
  volume_num: number;
  title: string;
  children: ChapterInfo[];
}

// 2. 在组件状态中添加：
const [volumeTree, setVolumeTree] = useState<VolumeTreeNode[]>([]);

// 3. 修改 loadChapters 函数：
const loadChapters = async () => {
  setLoading(true);
  try {
    const response = await axios.get<ProjectChaptersResponse>(`/api/chapters/project/${projectId}`);
    const data = response.data;
    
    setOutlineLevel(data.outline_level);
    setResponseMessage(data.message);
    setChapters(data.chapters || []);
    
    // 如果是卷级大纲，构建树形结构
    if (data.outline_level === 'volume' && data.chapters.length > 0) {
      // 获取大纲数据来构建完整的卷结构
      const outlineResponse = await axios.get(`/api/projects/${projectId}/outline?hierarchy=true`);
      const outline = outlineResponse.data;
      
      // 构建卷-章节树
      const tree: VolumeTreeNode[] = outline.chapters.map((vol: any) => ({
        volume_num: vol.chapter_num,
        title: vol.title,
        children: data.chapters.filter((ch: ChapterInfo) => ch.parent_id === vol.id)
      }));
      
      setVolumeTree(tree);
    } else {
      setVolumeTree([]);
    }
    
    if (data.outline_level === 'volume' && data.chapters.length === 0) {
      message.warning(data.message);
    }
  } catch (error) {
    message.error('加载章节列表失败');
  } finally {
    setLoading(false);
  }
};

// 4. 在渲染部分，替换章节列表的条件渲染：
{loading ? (
  <div style={{ textAlign: 'center', padding: 40 }}>
    <Spin />
  </div>
) : outlineLevel === 'volume' && chapters.length === 0 ? (
  <div style={{ padding: 24, textAlign: 'center' }}>
    <Text type="secondary">
      {responseMessage}
    </Text>
    <Divider />
    <Text type="secondary" style={{ fontSize: 12 }}>
      💡 提示：请先在"大纲编辑"Tab中将卷级大纲细化为章节大纲，<br/>
      或重新生成章级大纲后再进行正文编写。
    </Text>
  </div>
) : outlineLevel === 'volume' && volumeTree.length > 0 ? (
  /* 卷级大纲 - 树形结构 */
  <div style={{ padding: 16 }}>
    {volumeTree.map((volume) => (
      <div key={volume.volume_num} style={{ marginBottom: 16 }}>
        <div style={{ 
          padding: '8px 12px', 
          background: '#f0f0f0', 
          borderRadius: 4,
          marginBottom: 8,
          fontWeight: 'bold'
        }}>
          <FolderOutlined style={{ marginRight: 8 }} />
          第{volume.volume_num}卷: {volume.title}
        </div>
        {volume.children.length > 0 ? (
          <List
            size="small"
            dataSource={volume.children}
            renderItem={(item) => (
              <List.Item
                style={{ 
                  cursor: 'pointer',
                  background: selectedChapter?.outline_chapter_id === item.outline_chapter_id 
                    ? '#e6f7ff' 
                    : 'transparent',
                  padding: '8px 12px 8px 32px',
                  borderLeft: '2px solid #d9d9d9'
                }}
                onClick={() => handleSelectChapter(item)}
                actions={[
                  <Button
                    type="text"
                    size="small"
                    icon={<EditOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditChapterInfo(item);
                    }}
                  />,
                  <Popconfirm
                    title="确定删除此章节？"
                    description="删除后将无法恢复，包括已编写的正文内容"
                    onConfirm={(e) => {
                      e?.stopPropagation();
                      handleDeleteChapter(item.outline_chapter_id);
                    }}
                    onCancel={(e) => e?.stopPropagation()}
                    okText="删除"
                    cancelText="取消"
                  >
                    <Button
                      type="text"
                      size="small"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </Popconfirm>
                ]}
              >
                <List.Item.Meta
                  avatar={<FileOutlined />}
                  title={
                    <Space>
                      <Text>第{item.chapter_num}章</Text>
                      {getStatusTag(item.chapter?.status || 'not_started')}
                    </Space>
                  }
                  description={
                    <div>
                      <Paragraph ellipsis={{ rows: 1 }} style={{ margin: 0 }}>
                        {item.title}
                      </Paragraph>
                      {item.chapter && (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {item.chapter.word_count} 字
                        </Text>
                      )}
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <div style={{ padding: '12px 32px', color: '#999', fontSize: 12 }}>
            暂无章节
          </div>
        )}
      </div>
    ))}
  </div>
) : chapters.length === 0 ? (
  <div style={{ padding: 24, textAlign: 'center' }}>
    <Text type="secondary">
      暂无章节，请先在"大纲编辑"Tab中生成大纲
    </Text>
  </div>
) : (
  /* 章级大纲 - 平铺列表 */
  <List
    dataSource={chapters}
    renderItem={(item) => (
      // ... 保持原有的 List.Item 代码不变
    )}
  />
)}
