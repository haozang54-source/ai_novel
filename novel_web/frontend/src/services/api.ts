import axios from 'axios';

const API_BASE = '/api';

// 项目相关API
export const projectApi = {
  list: () => axios.get(`${API_BASE}/projects`),
  create: (data: any) => axios.post(`${API_BASE}/projects`, data),
  get: (id: number) => axios.get(`${API_BASE}/projects/${id}`),
  update: (id: number, data: any) => axios.put(`${API_BASE}/projects/${id}`, data),
  delete: (id: number) => axios.delete(`${API_BASE}/projects/${id}`),
};

// 大纲相关API
export const outlineApi = {
  get: (projectId: number) => axios.get(`${API_BASE}/projects/${projectId}/outline`),
  getWithHierarchy: (projectId: number) => axios.get(`${API_BASE}/projects/${projectId}/outline?hierarchy=true`),
  generate: (projectId: number, config: any) => axios.post(`${API_BASE}/projects/${projectId}/outline/generate`, config),
  updateChapter: (chapterId: number, data: any) => axios.put(`${API_BASE}/outline-chapters/${chapterId}`, data),
};

// 章节相关API
export const chapterApi = {
  getByOutlineChapter: (outlineChapterId: number) => 
    axios.get(`${API_BASE}/chapters/outline-chapter/${outlineChapterId}`),
  createOrUpdate: (outlineChapterId: number, data: any) => 
    axios.post(`${API_BASE}/chapters/outline-chapter/${outlineChapterId}`, data),
  delete: (chapterId: number) => 
    axios.delete(`${API_BASE}/chapters/${chapterId}`),
  getProjectChapters: (projectId: number) => 
    axios.get(`${API_BASE}/chapters/project/${projectId}`),
  
  // 大纲章节管理
  addOutlineChapter: (outlineId: number, data: any) => 
    axios.post(`${API_BASE}/chapters/outline/${outlineId}/chapters`, data),
  updateOutlineChapter: (outlineChapterId: number, data: any) => 
    axios.put(`${API_BASE}/chapters/outline-chapter/${outlineChapterId}`, data),
  deleteOutlineChapter: (outlineChapterId: number) => 
    axios.delete(`${API_BASE}/chapters/outline-chapter/${outlineChapterId}`),
};

// AI助手相关API
export const aiAssistantApi = {
  analyze: (data: any) => axios.post(`${API_BASE}/ai-assistant/analyze`, data),
  getKnowledgeBase: (projectId: number) => 
    axios.get(`${API_BASE}/ai-assistant/knowledge-base/${projectId}`),
};

// 人物相关API
export const characterApi = {
  list: (projectId: number) => axios.get(`${API_BASE}/characters/project/${projectId}`),
  create: (data: any) => axios.post(`${API_BASE}/characters`, data),
  get: (id: number) => axios.get(`${API_BASE}/characters/${id}`),
  update: (id: number, data: any) => axios.put(`${API_BASE}/characters/${id}`, data),
  delete: (id: number) => axios.delete(`${API_BASE}/characters/${id}`),
  
  // 关系管理
  createRelation: (characterId: number, data: any) => 
    axios.post(`${API_BASE}/characters/${characterId}/relations`, data),
  updateRelation: (characterId: number, relationId: number, data: any) => 
    axios.put(`${API_BASE}/characters/${characterId}/relations/${relationId}`, data),
  deleteRelation: (characterId: number, relationId: number) => 
    axios.delete(`${API_BASE}/characters/${characterId}/relations/${relationId}`),
};

// 世界观相关API
export const worldviewApi = {
  list: (projectId: number) => axios.get(`${API_BASE}/worldviews/project/${projectId}`),
  create: (data: any) => axios.post(`${API_BASE}/worldviews`, data),
  get: (id: number) => axios.get(`${API_BASE}/worldviews/${id}`),
  update: (id: number, data: any) => axios.put(`${API_BASE}/worldviews/${id}`, data),
  delete: (id: number) => axios.delete(`${API_BASE}/worldviews/${id}`),
};

// 地点相关API
export const locationApi = {
  list: (projectId: number) => axios.get(`${API_BASE}/locations/project/${projectId}`),
  create: (data: any) => axios.post(`${API_BASE}/locations`, data),
  get: (id: number) => axios.get(`${API_BASE}/locations/${id}`),
  update: (id: number, data: any) => axios.put(`${API_BASE}/locations/${id}`, data),
  delete: (id: number) => axios.delete(`${API_BASE}/locations/${id}`),
};

// 物品相关API
export const itemApi = {
  list: (projectId: number) => axios.get(`${API_BASE}/items/project/${projectId}`),
  create: (data: any) => axios.post(`${API_BASE}/items`, data),
  get: (id: number) => axios.get(`${API_BASE}/items/${id}`),
  update: (id: number, data: any) => axios.put(`${API_BASE}/items/${id}`, data),
  delete: (id: number) => axios.delete(`${API_BASE}/items/${id}`),
};

// 伏笔相关API
export const foreshadowingApi = {
  list: (projectId: number) => axios.get(`${API_BASE}/foreshadowings/project/${projectId}`),
  create: (data: any) => axios.post(`${API_BASE}/foreshadowings`, data),
  get: (id: number) => axios.get(`${API_BASE}/foreshadowings/${id}`),
  update: (id: number, data: any) => axios.put(`${API_BASE}/foreshadowings/${id}`, data),
  delete: (id: number) => axios.delete(`${API_BASE}/foreshadowings/${id}`),
};

// 文风设定相关API
export const writingStyleApi = {
  get: (projectId: number) => axios.get(`${API_BASE}/writing-styles/project/${projectId}`),
  createOrUpdate: (projectId: number, data: any) => 
    axios.post(`${API_BASE}/writing-styles/project/${projectId}`, data),
  delete: (id: number) => axios.delete(`${API_BASE}/writing-styles/${id}`),
};

export default {
  projectApi,
  outlineApi,
  chapterApi,
  aiAssistantApi,
  characterApi,
  worldviewApi,
  locationApi,
  itemApi,
  foreshadowingApi,
  writingStyleApi,
};
