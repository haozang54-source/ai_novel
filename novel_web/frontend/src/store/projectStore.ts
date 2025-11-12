import { create } from 'zustand';
import { projectApi } from '../services/api';
import type { Project } from '../types';

interface ProjectStore {
  projects: Project[];
  currentProject: Project | null;
  loading: boolean;
  fetchProjects: () => Promise<void>;
  createProject: (data: Partial<Project>) => Promise<Project>;
  selectProject: (id: number) => void;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  currentProject: null,
  loading: false,
  
  fetchProjects: async () => {
    set({ loading: true });
    try {
      const response = await projectApi.list();
      set({ projects: response.data, loading: false });
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      set({ loading: false });
    }
  },
  
  createProject: async (data) => {
    const response = await projectApi.create(data);
    const newProject = response.data;
    set(state => ({ projects: [newProject, ...state.projects] }));
    return newProject;
  },
  
  selectProject: (id) => {
    const project = get().projects.find(p => p.id === id);
    set({ currentProject: project || null });
  },
}));
