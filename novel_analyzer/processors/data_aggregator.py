"""
数据聚合器 - 将章节分析结果聚合为分类数据
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class DataAggregator:
    """数据聚合器，将章节JSON聚合为分类数据"""
    
    def __init__(self, chapter_summaries_dir: str):
        """
        初始化聚合器
        
        Args:
            chapter_summaries_dir: 章节摘要JSON文件目录
        """
        self.chapter_dir = Path(chapter_summaries_dir)
        if not self.chapter_dir.exists():
            raise ValueError(f"章节摘要目录不存在: {chapter_summaries_dir}")
    
    def load_all_chapters(self) -> List[Dict]:
        """加载所有章节JSON文件"""
        chapters = []
        chapter_files = sorted(self.chapter_dir.glob("chapter_*.json"))
        
        for file_path in chapter_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    chapter_data = json.load(f)
                    chapters.append(chapter_data)
            except Exception as e:
                print(f"⚠️  加载章节文件失败 {file_path.name}: {e}")
        
        return chapters
    
    def aggregate_characters(self, chapters: List[Dict]) -> List[Dict]:
        """
        聚合角色数据
        
        Returns:
            角色列表，每个角色包含所有出现章节的信息
        """
        characters_dict = {}
        
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number')
            chapter_title = chapter.get('chapter_title', f'第{chapter_num}章')
            
            for char in chapter.get('characters', []):
                name = char.get('name')
                if not name:
                    continue
                
                if name not in characters_dict:
                    characters_dict[name] = {
                        'name': name,
                        'role': char.get('role', 'unknown'),
                        'first_appearance_chapter': chapter_num,
                        'appearance_chapters': [],
                        'status_changes': [],
                        'relationships': [],
                        'appearance_traits': set(),
                        'personality_traits': set()
                    }
                
                # 记录出现章节
                characters_dict[name]['appearance_chapters'].append({
                    'chapter_number': chapter_num,
                    'chapter_title': chapter_title,
                    'is_first_appearance': char.get('first_appearance', False)
                })
                
                # 聚合状态变化
                for status in char.get('status_changes', []):
                    if status:
                        characters_dict[name]['status_changes'].append({
                            'chapter': chapter_num,
                            'change': status
                        })
                
                # 聚合关系
                for rel in char.get('relationships', []):
                    if rel:
                        characters_dict[name]['relationships'].append({
                            'chapter': chapter_num,
                            **rel
                        })
                
                # 聚合特征
                for trait in char.get('appearance_traits', []):
                    if trait:
                        characters_dict[name]['appearance_traits'].add(trait)
                
                for trait in char.get('personality_traits', []):
                    if trait:
                        characters_dict[name]['personality_traits'].add(trait)
        
        # 转换set为list
        characters_list = []
        for char_data in characters_dict.values():
            char_data['appearance_traits'] = list(char_data['appearance_traits'])
            char_data['personality_traits'] = list(char_data['personality_traits'])
            char_data['total_appearances'] = len(char_data['appearance_chapters'])
            characters_list.append(char_data)
        
        # 按出场次数排序
        characters_list.sort(key=lambda x: x['total_appearances'], reverse=True)
        
        return characters_list
    
    def aggregate_locations(self, chapters: List[Dict]) -> List[Dict]:
        """
        聚合地点数据
        
        Returns:
            地点列表
        """
        locations_dict = {}
        
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number')
            chapter_title = chapter.get('chapter_title', f'第{chapter_num}章')
            
            for loc in chapter.get('locations', []):
                name = loc.get('name')
                if not name:
                    continue
                
                if name not in locations_dict:
                    locations_dict[name] = {
                        'name': name,
                        'type': loc.get('type', 'unknown'),
                        'first_appearance_chapter': chapter_num,
                        'appearance_chapters': [],
                        'descriptions': []
                    }
                
                locations_dict[name]['appearance_chapters'].append({
                    'chapter_number': chapter_num,
                    'chapter_title': chapter_title,
                    'is_first_appearance': loc.get('first_appearance', False)
                })
                
                desc = loc.get('description')
                if desc:
                    locations_dict[name]['descriptions'].append({
                        'chapter': chapter_num,
                        'description': desc
                    })
        
        locations_list = list(locations_dict.values())
        locations_list.sort(key=lambda x: len(x['appearance_chapters']), reverse=True)
        
        return locations_list
    
    def aggregate_events(self, chapters: List[Dict]) -> List[Dict]:
        """
        聚合事件数据
        
        Returns:
            事件列表
        """
        events_list = []
        
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number')
            chapter_title = chapter.get('chapter_title', f'第{chapter_num}章')
            
            for event in chapter.get('events', []):
                events_list.append({
                    'chapter_number': chapter_num,
                    'chapter_title': chapter_title,
                    'type': event.get('type', 'unknown'),
                    'description': event.get('description', ''),
                    'importance': event.get('importance', 'medium'),
                    'emotional_tone': event.get('emotional_tone', ''),
                    'participants': event.get('participants', [])
                })
        
        return events_list
    
    def aggregate_world_elements(self, chapters: List[Dict]) -> Dict[str, List[Dict]]:
        """
        聚合世界观元素
        
        Returns:
            按类型分类的世界观元素字典
        """
        world_elements = defaultdict(list)
        seen_elements = set()
        
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number')
            
            for element in chapter.get('world_elements', []):
                elem_type = element.get('type', 'unknown')
                elem_name = element.get('element', '')
                
                # 去重（基于类型和名称）
                key = (elem_type, elem_name)
                if key in seen_elements:
                    continue
                seen_elements.add(key)
                
                world_elements[elem_type].append({
                    'element': elem_name,
                    'details': element.get('details', ''),
                    'first_mentioned_chapter': chapter_num
                })
        
        return dict(world_elements)
    
    def aggregate_writing_styles(self, chapters: List[Dict]) -> Dict[str, Any]:
        """
        聚合写作风格信息
        
        Returns:
            写作风格统计
        """
        perspectives = defaultdict(int)
        key_phrases = []
        emotional_intensities = defaultdict(int)
        description_focuses = defaultdict(int)
        
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number')
            style = chapter.get('writing_style_notes', {})
            
            # 统计叙事视角
            perspective = style.get('narrative_perspective', 'unknown')
            perspectives[perspective] += 1
            
            # 收集关键短语
            for phrase in style.get('key_phrases', []):
                key_phrases.append({
                    'chapter': chapter_num,
                    'phrase': phrase
                })
            
            # 统计情感强度
            intensity = style.get('emotional_intensity', 'unknown')
            emotional_intensities[intensity] += 1
            
            # 统计描写重点
            for focus in style.get('description_focus', []):
                description_focuses[focus] += 1
        
        return {
            'narrative_perspectives': dict(perspectives),
            'key_phrases': key_phrases,
            'emotional_intensities': dict(emotional_intensities),
            'description_focuses': dict(description_focuses)
        }
    
    def aggregate_plot_arcs(self, chapters: List[Dict]) -> List[Dict]:
        """
        聚合情节线索（基于章节摘要）
        
        Returns:
            情节线索列表
        """
        plot_arcs = []
        
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number')
            summary = chapter.get('chapter_summary', {})
            
            plot_arcs.append({
                'chapter_number': chapter_num,
                'chapter_title': summary.get('title', chapter.get('chapter_title', '')),
                'main_content': summary.get('main_content', ''),
                'key_points': summary.get('key_points', []),
                'chapter_purpose': summary.get('chapter_purpose', ''),
                'word_count': chapter.get('word_count', 0)
            })
        
        return plot_arcs
    
    def create_aggregated_data(self) -> Dict[str, Any]:
        """
        创建完整的聚合数据
        
        Returns:
            包含所有聚合分类的字典
        """
        print("📚 加载所有章节...")
        chapters = self.load_all_chapters()
        print(f"✅ 成功加载 {len(chapters)} 个章节")
        
        print("👥 聚合角色数据...")
        characters = self.aggregate_characters(chapters)
        print(f"✅ 聚合 {len(characters)} 个角色")
        
        print("🗺️  聚合地点数据...")
        locations = self.aggregate_locations(chapters)
        print(f"✅ 聚合 {len(locations)} 个地点")
        
        print("📖 聚合事件数据...")
        events = self.aggregate_events(chapters)
        print(f"✅ 聚合 {len(events)} 个事件")
        
        print("🌍 聚合世界观元素...")
        world_elements = self.aggregate_world_elements(chapters)
        total_elements = sum(len(v) for v in world_elements.values())
        print(f"✅ 聚合 {total_elements} 个世界观元素")
        
        print("✍️  聚合写作风格...")
        writing_styles = self.aggregate_writing_styles(chapters)
        print(f"✅ 聚合写作风格统计")
        
        print("📊 聚合情节线索...")
        plot_arcs = self.aggregate_plot_arcs(chapters)
        print(f"✅ 聚合 {len(plot_arcs)} 个情节线索")
        
        return {
            'metadata': {
                'total_chapters': len(chapters),
                'total_characters': len(characters),
                'total_locations': len(locations),
                'total_events': len(events),
                'total_world_elements': total_elements
            },
            'characters': characters,
            'locations': locations,
            'events': events,
            'world_elements': world_elements,
            'writing_styles': writing_styles,
            'plot_arcs': plot_arcs,
            'raw_chapters': chapters
        }
    
    def save_aggregated_data(self, output_dir: str, data: Dict[str, Any] = None):
        """
        保存聚合数据到分类文件
        
        Args:
            output_dir: 输出目录
            data: 聚合数据（如果为None则重新生成）
        """
        if data is None:
            data = self.create_aggregated_data()
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 保存聚合数据到 {output_dir}...")
        
        # 保存各个分类
        categories = {
            'characters.json': data['characters'],
            'locations.json': data['locations'],
            'events.json': data['events'],
            'world_elements.json': data['world_elements'],
            'writing_styles.json': data['writing_styles'],
            'plot_arcs.json': data['plot_arcs'],
            'metadata.json': data['metadata']
        }
        
        for filename, content in categories.items():
            file_path = output_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            size_kb = file_path.stat().st_size / 1024
            print(f"  ✅ {filename}: {size_kb:.2f} KB")
        
        print(f"\n✨ 聚合数据保存完成！")
