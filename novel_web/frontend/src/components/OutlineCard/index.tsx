import { Card, Tag, Space, Button, Collapse } from 'antd';
import { CheckCircleOutlined, ExclamationCircleOutlined, ClockCircleOutlined, PlusOutlined, DownOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { OutlineNode } from '../../types';
import { useState } from 'react';

const { Panel } = Collapse;

interface Props {
  node: OutlineNode;
  onEdit?: (node: OutlineNode) => void;
  onDelete?: (node: OutlineNode) => void;
  onAddChild?: (parentId: number) => void;
  isVolume?: boolean;
}

const statusConfig = {
  pending: { text: '待审阅', color: 'default', icon: <ClockCircleOutlined /> },
  approved: { text: '已确认', color: 'success', icon: <CheckCircleOutlined /> },
  need_revision: { text: '需修改', color: 'warning', icon: <ExclamationCircleOutlined /> },
};

export default function OutlineCard({ node, onEdit, onDelete, onAddChild, isVolume }: Props) {
  const status = statusConfig[node.review_status] || statusConfig.pending;
  const unitLabel = node.outline_type === 'volume' ? '卷' : '章';
  const [activeKey, setActiveKey] = useState<string | string[]>([]);

  const hasChildren = node.children && node.children.length > 0;

  // 如果是卷且有子章节或者可以添加子章节，使用折叠面板
  if (node.outline_type === 'volume' && (hasChildren || onAddChild)) {
    return (
      <Card
        style={{ marginBottom: 16 }}
        title={
          <Space wrap>
            <span>
              {node.chapter_num ? `第${node.chapter_num}${unitLabel}: ` : ''}
              {node.title}
            </span>
            <Tag color={status.color} icon={status.icon}>{status.text}</Tag>
            {onEdit && (
              <Button 
                type="link" 
                size="small" 
                icon={<EditOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(node);
                }}
              >
                编辑
              </Button>
            )}
            {onDelete && (
              <Button 
                type="link" 
                size="small" 
                danger
                icon={<DeleteOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(node);
                }}
              >
                删除
              </Button>
            )}
          </Space>
        }
        extra={
          onAddChild && (
            <Button
              type="primary"
              size="small"
              icon={<PlusOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onAddChild(node.id);
              }}
            >
              添加章节
            </Button>
          )
        }
      >
        {node.positioning && (
          <p><strong>定位:</strong> {node.positioning}</p>
        )}
        {node.length && (
          <p><strong>篇幅:</strong> {node.length}</p>
        )}
        <p><strong>摘要:</strong> {node.summary}</p>

        {node.core_tasks && node.core_tasks.length > 0 && (
          <div style={{ marginTop: 8 }}>
            <strong>核心任务:</strong>
            <Space wrap style={{ marginTop: 8 }}>
              {node.core_tasks.map((task, idx) => (
                <Tag key={`task-${idx}`} color="blue">{task}</Tag>
              ))}
            </Space>
          </div>
        )}

        {hasChildren && (
          <Collapse
            activeKey={activeKey}
            onChange={setActiveKey}
            style={{ marginTop: 16 }}
            expandIcon={({ isActive }) => <DownOutlined rotate={isActive ? 180 : 0} />}
          >
            <Panel header={`章节列表 (共${node.children!.length}章)`} key="1">
              <div style={{ paddingLeft: 16 }}>
                {node.children!.map((child) => (
                  <OutlineCard
                    key={child.id}
                    node={child}
                    onEdit={onEdit}
                    onDelete={onDelete}
                  />
                ))}
              </div>
            </Panel>
          </Collapse>
        )}
      </Card>
    );
  }

  // 普通章节卡片
  return (
    <Card
      style={{ marginBottom: 16 }}
      title={
        <Space wrap>
          <span>
            {node.chapter_num ? `第${node.chapter_num}${unitLabel}: ` : ''}
            {node.title}
          </span>
          <Tag color={status.color} icon={status.icon}>{status.text}</Tag>
          {onEdit && (
            <Button 
              type="link" 
              size="small" 
              icon={<EditOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onEdit(node);
              }}
            >
              编辑
            </Button>
          )}
          {onDelete && (
            <Button 
              type="link" 
              size="small" 
              danger
              icon={<DeleteOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onDelete(node);
              }}
            >
              删除
            </Button>
          )}
        </Space>
      }
    >
      {node.positioning && (
        <p><strong>定位:</strong> {node.positioning}</p>
      )}
      {node.length && (
        <p><strong>篇幅:</strong> {node.length}</p>
      )}
      <p><strong>摘要:</strong> {node.summary}</p>

      {node.core_tasks && node.core_tasks.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <strong>核心任务:</strong>
          <Space wrap style={{ marginTop: 8 }}>
            {node.core_tasks.map((task, idx) => (
              <Tag key={`task-${idx}`} color="blue">{task}</Tag>
            ))}
          </Space>
        </div>
      )}

      {node.key_turns && node.key_turns.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <strong>关键转折:</strong>
          <Space wrap style={{ marginTop: 8 }}>
            {node.key_turns.map((turn, idx) => (
              <Tag key={`turn-${idx}`} color="purple">{turn}</Tag>
            ))}
          </Space>
        </div>
      )}

      <p style={{ marginTop: 8 }}><strong>核心冲突:</strong> {node.conflicts}</p>
      <p><strong>情感基调:</strong> {node.emotional_beat}</p>

      {node.character_growth && (
        <p><strong>人物成长:</strong> {node.character_growth}</p>
      )}

      {node.key_events && node.key_events.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <strong>关键事件:</strong>
          <Space wrap style={{ marginTop: 8 }}>
            {node.key_events.map((event, idx) => (
              <Tag key={`event-${idx}`}>{event}</Tag>
            ))}
          </Space>
        </div>
      )}
    </Card>
  );
}
