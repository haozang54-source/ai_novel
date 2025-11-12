import { create } from 'zustand';
import { outlineApi } from '../services/api';
import type { Outline, OutlineChapter } from '../types';

interface OutlineStore {
  outline: Outline | null;
  selectedChapter: OutlineChapter | null;
  isGenerating: boolean;
  
  fetchOutline: (projectId: number) => Promise<void>;
  generateOutline: (projectId: number, config: any) => Promise<void>;
  updateChapter: (chapterId: number, data: Partial<OutlineChapter>) => Promise<void>;
  selectChapter: (chapter: OutlineChapter | null) => void;
  setGenerating: (isGenerating: boolean) => void;
}

export const useOutlineStore = create<OutlineStore>((set) => ({
  outline: null,
  selectedChapter: null,
  isGenerating: false,
  
  fetchOutline: async (projectId) => {
    try {
      // 如果大纲是卷级大纲，请求层级结构
      const response = await outlineApi.get(projectId);
      const outline = response.data;
      
      // 如果是卷级大纲，重新请求带层级结构的数据
      if (outline.outline_level === 'volume') {
        const hierarchyResponse = await outlineApi.getWithHierarchy(projectId);
        set({ outline: hierarchyResponse.data });
      } else {
        set({ outline });
      }
    } catch (error) {
      console.error('Failed to fetch outline:', error);
    }
  },
  
  generateOutline: async (projectId, config) => {
    set({ isGenerating: true });
    try {
      await outlineApi.generate(projectId, config);
      // 生成完成后重新获取大纲
      const response = await outlineApi.get(projectId);
      set({ outline: response.data, isGenerating: false });
    } catch (error) {
      console.error('Failed to generate outline:', error);
      set({ isGenerating: false });
    }
  },
  
  updateChapter: async (chapterId, data) => {
    await outlineApi.updateChapter(chapterId, data);
    set(state => ({
      outline: state.outline ? {
        ...state.outline,
        chapters: state.outline.chapters.map(ch => 
          ch.id === chapterId ? { ...ch, ...data } : ch
        )
      } : null
    }));
  },
  
  selectChapter: (chapter) => {
    set({ selectedChapter: chapter });
  },
  
  setGenerating: (isGenerating) => {
    set({ isGenerating });
  },
}));
