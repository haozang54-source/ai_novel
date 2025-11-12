import { useState, useCallback, useEffect } from 'react';
import { FloatButton, message, Badge } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import { useTextSelection, TextSelectionInfo } from '../hooks/useTextSelection';
import { useAIAssistant } from '../contexts/AIAssistantContext';

interface GlobalAIAssistantProps {
  projectId: number;
  enabled?: boolean;
}

/**
 * 全局AI助手浮动按钮
 * 始终显示在右下角，当选中文本时会有提示
 */
export default function GlobalAIAssistant({ projectId, enabled = true }: GlobalAIAssistantProps) {
  const { showAIAssistant } = useAIAssistant();
  const [currentSelection, setCurrentSelection] = useState<TextSelectionInfo | null>(null);
  const [textValue, setTextValue] = useState('');
  const [textRange, setTextRange] = useState<{ start: number; end: number } | null>(null);

  const handleSelect = useCallback((info: TextSelectionInfo) => {
    setCurrentSelection(info);

    // 获取完整的文本内容
    const element = info.element;
    let fullText = '';
    let startOffset = 0;
    let endOffset = 0;

    if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
      const input = element as HTMLTextAreaElement | HTMLInputElement;
      fullText = input.value;
      startOffset = input.selectionStart || 0;
      endOffset = input.selectionEnd || 0;
    } else {
      // ContentEditable 或其他情况
      fullText = element.textContent || '';
      // 尝试获取选区在文本中的位置
      const range = info.range;
      const preRange = range.cloneRange();
      preRange.selectNodeContents(element);
      preRange.setEnd(range.startContainer, range.startOffset);
      startOffset = preRange.toString().length;
      endOffset = startOffset + info.text.length;
    }

    setTextValue(fullText);
    setTextRange({ start: startOffset, end: endOffset });
  }, []);

  const handleClear = useCallback(() => {
    setCurrentSelection(null);
    setTextRange(null);
  }, []);

  const { selection } = useTextSelection({
    onSelect: handleSelect,
    onClear: handleClear,
    enabled
  });

  const handleAIClick = useCallback(() => {
    // 允许在没有选中文本时也打开AI助手
    const element = currentSelection?.element;
    const isEditable = element && (
      element.tagName === 'TEXTAREA' || 
      element.tagName === 'INPUT' || 
      element.isContentEditable ||
      element.closest('[contenteditable="true"]') !== null
    );

    const contextBefore = currentSelection ? textValue.substring(
      Math.max(0, (textRange?.start || 0) - 200),
      textRange?.start || 0
    ) : '';
    const contextAfter = currentSelection ? textValue.substring(
      textRange?.end || 0,
      Math.min(textValue.length, (textRange?.end || 0) + 200)
    ) : '';

    showAIAssistant({
      selectedText: currentSelection?.text || '',
      projectId,
      contextBefore,
      contextAfter,
      onApply: (newText: string) => {
        if (!currentSelection) {
          // 没有选中文本时，复制到剪贴板
          navigator.clipboard.writeText(newText).then(() => {
            message.success('AI结果已复制到剪贴板');
          }).catch(() => {
            message.error('复制到剪贴板失败');
          });
          return;
        }

        if (isEditable && textRange && element) {
          // 可编辑元素：直接应用到文本框
          if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
            const input = element as HTMLTextAreaElement | HTMLInputElement;
            const before = textValue.substring(0, textRange.start);
            const after = textValue.substring(textRange.end);
            const newValue = before + newText + after;
            
            // 触发React的onChange事件
            const isTextarea = element.tagName === 'TEXTAREA';
            const prototype = isTextarea 
              ? window.HTMLTextAreaElement.prototype 
              : window.HTMLInputElement.prototype;
            
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set;
            
            if (nativeInputValueSetter) {
              nativeInputValueSetter.call(input, newValue);
              
              // 触发input事件让React感知变化
              const inputEvent = new Event('input', { bubbles: true });
              input.dispatchEvent(inputEvent);
              
              // 触发change事件
              const changeEvent = new Event('change', { bubbles: true });
              input.dispatchEvent(changeEvent);
            } else {
              // 降级方案：直接设置value
              input.value = newValue;
            }
            
            // 设置光标位置到新文本末尾
            const newCursorPos = textRange.start + newText.length;
            input.setSelectionRange(newCursorPos, newCursorPos);
            input.focus();
            
            message.success('AI修改已应用');
          } else if (element.isContentEditable || element.closest('[contenteditable="true"]')) {
            // ContentEditable
            const range = currentSelection.range;
            range.deleteContents();
            range.insertNode(document.createTextNode(newText));
            
            message.success('AI修改已应用');
          }
        } else {
          // 不可编辑元素：复制到剪贴板
          navigator.clipboard.writeText(newText).then(() => {
            message.success('AI结果已复制到剪贴板');
          }).catch(() => {
            message.error('复制到剪贴板失败');
          });
        }

        // 清空选中状态
        setCurrentSelection(null);
        setTextRange(null);
      },
      onCancel: () => {
        // 取消后不清空选中，可以继续使用
      }
    });
  }, [currentSelection, textRange, textValue, projectId, showAIAssistant]);

  return (
    <Badge dot={!!currentSelection} offset={[-5, 5]}>
      <FloatButton
        icon={<RobotOutlined />}
        type={currentSelection ? 'primary' : 'default'}
        tooltip={currentSelection ? '点击使用AI助手处理选中文本' : 'AI助手'}
        onClick={handleAIClick}
        style={{
          right: 24,
          bottom: 24,
          zIndex: 10000, // 确保始终在最上层，高于Modal(1000)、Drawer(1000)等
        }}
      />
    </Badge>
  );
}
