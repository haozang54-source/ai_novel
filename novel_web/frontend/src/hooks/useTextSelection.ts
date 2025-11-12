import { useEffect, useCallback, useRef, useState } from 'react';
import { FloatButton } from 'antd';
import { RobotOutlined } from '@ant-design/icons';

export interface TextSelectionInfo {
  text: string;
  element: HTMLElement;
  range: Range;
  rect: DOMRect;
}

interface UseTextSelectionOptions {
  onSelect?: (info: TextSelectionInfo) => void;
  onClear?: () => void;
  enabled?: boolean;
}

/**
 * 监听文本选择的Hook
 * 当用户在可编辑元素中选中文本时，会触发回调
 */
export function useTextSelection(options: UseTextSelectionOptions = {}) {
  const { onSelect, onClear, enabled = true } = options;
  const [selection, setSelection] = useState<TextSelectionInfo | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const handleSelectionChange = useCallback(() => {
    if (!enabled) return;

    // 清除之前的延迟
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // 延迟处理，避免频繁触发
    timeoutRef.current = setTimeout(() => {
      const windowSelection = window.getSelection();
      
      if (!windowSelection || windowSelection.rangeCount === 0) {
        setSelection(null);
        onClear?.();
        return;
      }

      const selectedText = windowSelection.toString().trim();
      
      if (!selectedText) {
        setSelection(null);
        onClear?.();
        return;
      }

      const range = windowSelection.getRangeAt(0);
      let element = range.commonAncestorContainer as Node;
      
      // 如果是文本节点，获取其父元素
      if (element.nodeType === Node.TEXT_NODE) {
        element = element.parentElement as HTMLElement;
      }
      
      if (!element || !(element instanceof HTMLElement)) {
        setSelection(null);
        onClear?.();
        return;
      }

      // 优先检查 document.activeElement（当前焦点元素）
      const activeElement = document.activeElement;
      let targetElement: HTMLElement = element as HTMLElement;

      // 检查焦点元素是否是可编辑的
      if (activeElement && 
          (activeElement.tagName === 'TEXTAREA' || 
           activeElement.tagName === 'INPUT' ||
           (activeElement as HTMLElement).isContentEditable)) {
        targetElement = activeElement as HTMLElement;
      } else {
        // 从选中的元素向上查找可编辑元素
        const editableElement = (element as HTMLElement).closest('textarea, input, [contenteditable="true"]');
        if (editableElement) {
          targetElement = editableElement as HTMLElement;
        } else {
          // 检查元素本身是否可编辑
          const htmlElement = element as HTMLElement;
          if (htmlElement.isContentEditable || 
              htmlElement.tagName === 'TEXTAREA' || 
              htmlElement.tagName === 'INPUT') {
            targetElement = htmlElement;
          }
          // 如果不可编辑，仍然允许选择（用于复制到剪贴板）
        }
      }

      const rect = range.getBoundingClientRect();
      
      const info: TextSelectionInfo = {
        text: selectedText,
        element: targetElement,
        range,
        rect
      };

      console.log('Text selected:', {
        text: selectedText,
        element: targetElement.tagName,
        activeElement: document.activeElement?.tagName,
        isEditable: targetElement.tagName === 'TEXTAREA' || 
                    targetElement.tagName === 'INPUT' || 
                    targetElement.isContentEditable
      });

      setSelection(info);
      onSelect?.(info);
    }, 100);
  }, [enabled, onSelect, onClear]);

  useEffect(() => {
    if (!enabled) return;

    document.addEventListener('selectionchange', handleSelectionChange);
    document.addEventListener('mouseup', handleSelectionChange);

    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
      document.removeEventListener('mouseup', handleSelectionChange);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [enabled, handleSelectionChange]);

  return { selection, clearSelection: () => setSelection(null) };
}
