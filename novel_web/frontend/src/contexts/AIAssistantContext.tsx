import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { FloatButton, message } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import AIAssistantPanel from '../components/AIAssistantPanel';

interface AIAssistantContextType {
  showAIAssistant: (params: {
    selectedText: string;
    projectId: number;
    contextBefore?: string;
    contextAfter?: string;
    chapterId?: number;
    onApply: (newText: string) => void;
    onCancel?: () => void;
  }) => void;
  hideAIAssistant: () => void;
}

const AIAssistantContext = createContext<AIAssistantContextType | undefined>(undefined);

export const useAIAssistant = () => {
  const context = useContext(AIAssistantContext);
  if (!context) {
    throw new Error('useAIAssistant must be used within AIAssistantProvider');
  }
  return context;
};

interface AIAssistantProviderProps {
  children: React.ReactNode;
}

export const AIAssistantProvider: React.FC<AIAssistantProviderProps> = ({ children }) => {
  const [visible, setVisible] = useState(false);
  const [params, setParams] = useState<{
    selectedText: string;
    projectId: number;
    contextBefore?: string;
    contextAfter?: string;
    chapterId?: number;
    onApply: (newText: string) => void;
    onCancel?: () => void;
  } | null>(null);

  const showAIAssistant = useCallback((newParams: typeof params) => {
    // 允许在没有选中文本时也打开AI助手
    setParams(newParams);
    setVisible(true);
  }, []);

  const hideAIAssistant = useCallback(() => {
    setVisible(false);
    setTimeout(() => setParams(null), 300); // 等待动画结束后清空参数
  }, []);

  const handleApply = useCallback((newText: string) => {
    if (params?.onApply) {
      params.onApply(newText);
    }
  }, [params]);

  const handleCancel = useCallback(() => {
    if (params?.onCancel) {
      params.onCancel();
    }
  }, [params]);

  return (
    <AIAssistantContext.Provider value={{ showAIAssistant, hideAIAssistant }}>
      {children}
      
      {/* AI助手面板 */}
      {params && (
        <AIAssistantPanel
          visible={visible}
          onClose={hideAIAssistant}
          projectId={params.projectId}
          selectedText={params.selectedText}
          contextBefore={params.contextBefore}
          contextAfter={params.contextAfter}
          chapterId={params.chapterId}
          onApply={handleApply}
          onCancel={handleCancel}
        />
      )}
    </AIAssistantContext.Provider>
  );
};
