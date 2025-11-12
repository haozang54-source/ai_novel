export interface Project {
  id: number;
  title: string;
  theme: string;
  genre: string;
  target_length: number;
  status: 'draft' | 'outlining' | 'writing' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface Outline {
  id: number;
  project_id: number;
  story_concept: string;
  version: number;
  status: 'draft' | 'confirmed';
  ai_generated: boolean;
  outline_level: 'volume' | 'chapter';
  created_at: string;
  chapters: OutlineNode[];
}

export interface OutlineNode {
  id: number;
  outline_id: number;
  parent_id?: number;  // 父节点ID（卷-章节关系）
  chapter_num: number;
  title: string;
  summary: string;
  key_events: string[];
  conflicts: string;
  emotional_beat: string;
  positioning?: string;
  length?: string;
  core_tasks?: string[];
  key_turns?: string[];
  character_growth?: string;
  outline_type: 'volume' | 'chapter';
  review_status: 'pending' | 'approved' | 'need_revision';
  order_index: number;
  children?: OutlineNode[];  // 子节点（用于卷包含章节）
}

// 别名，向后兼容
export type OutlineChapter = OutlineNode;

// 创作设定类型
export interface WritingStyle {
  id: number;
  project_id: number;
  narrative_perspective?: string;
  language_style?: string;
  dialogue_style?: string;
  description_density?: string;
  custom_notes?: string;
  style_samples: Array<{ scene_type: string; sample: string }>;
  ai_weight: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Worldview {
  id: number;
  project_id: number;
  parent_id?: number;
  category: string;
  title: string;
  description?: string;
  tags: string[];
  importance: number;
  ai_weight: number;
  level: number;
  order_index: number;
  children?: Worldview[];
  created_at: string;
  updated_at: string;
}

export interface Character {
  id: number;
  project_id: number;
  name: string;
  alias: string[];
  avatar_url?: string;
  role_type?: string;
  gender?: string;
  age?: string;
  appearance?: string;
  personality?: string;
  background?: string;
  abilities: string[];
  goals?: string;
  conflicts?: string;
  character_arc?: string;
  key_moments: Array<{ chapter: number; event: string; change: string }>;
  tags: string[];
  importance: number;
  ai_weight: number;
  status: string;
  current_location_id?: number;
  relations?: CharacterRelation[];
  created_at: string;
  updated_at: string;
}

export interface CharacterRelation {
  id: number;
  from_character_id: number;
  to_character_id: number;
  relation_type?: string;
  description?: string;
  intimacy: number;
  start_chapter?: number;
  end_chapter?: number;
  relation_changes: Array<{ chapter: number; event: string; before: string; after: string }>;
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: number;
  project_id: number;
  parent_id?: number;
  name: string;
  location_type?: string;
  description?: string;
  map_image_url?: string;
  coordinates?: { x: number; y: number };
  climate?: string;
  terrain?: string;
  special_features?: string;
  tags: string[];
  importance: number;
  ai_weight: number;
  level: number;
  order_index: number;
  first_appearance?: number;
  appearance_chapters: number[];
  children?: Location[];
  created_at: string;
  updated_at: string;
}

export interface Item {
  id: number;
  project_id: number;
  name: string;
  category?: string;
  image_url?: string;
  description?: string;
  appearance?: string;
  abilities?: string;
  origin?: string;
  level?: string;
  rarity?: string;
  attributes: Record<string, any>;
  current_owner_id?: number;
  ownership_history: Array<{ chapter: number; from?: number; to?: number; how: string }>;
  first_appearance?: number;
  appearance_chapters: number[];
  status: string;
  location_id?: number;
  tags: string[];
  importance: number;
  ai_weight: number;
  created_at: string;
  updated_at: string;
}

export interface Foreshadowing {
  id: number;
  project_id: number;
  title: string;
  description?: string;
  category?: string;
  planted_chapter?: number;
  planted_content?: string;
  planted_method?: string;
  planned_reveal_chapter?: number;
  actual_reveal_chapter?: number;
  reveal_content?: string;
  status: 'planted' | 'revealed' | 'abandoned';
  related_characters: number[];
  related_items: number[];
  related_locations: number[];
  importance: number;
  urgency: number;
  ai_reminder?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}
