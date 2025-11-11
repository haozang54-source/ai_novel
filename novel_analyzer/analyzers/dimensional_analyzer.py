"""
维度分析器 - 策略2：分类并行处理
按不同维度（角色、情节、世界观、风格）分别处理所有章节数据
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class DimensionalAnalyzer:
    """维度分析器 - 多维度并行分析"""
    
    def __init__(self, llm, config: dict, aggregated_data: Dict[str, Any], output_dir: str):
        """
        初始化维度分析器
        
        Args:
            llm: LLM实例
            config: 配置字典
            aggregated_data: 聚合数据（来自DataAggregator）
            output_dir: 输出目录
        """
        self.llm = llm
        self.config = config
        self.data = aggregated_data
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置参数
        self.retry_times = config.get('extraction', {}).get('retry_times', 3)
        self.timeout = config.get('extraction', {}).get('timeout', 120)
    
    def analyze_all_dimensions(self) -> Dict[str, Any]:
        """
        并行分析所有维度
        
        Returns:
            包含所有维度分析结果的字典
        """
        print("\n" + "="*60)
        print("🎯 策略2：多维度并行分析")
        print("="*60)
        
        results = {}
        
        # 维度1: 角色线
        print("\n👥 维度1：角色分析...")
        results['character_dimension'] = self.analyze_character_dimension()
        
        # 维度2: 情节线
        print("\n📖 维度2：情节分析...")
        results['plot_dimension'] = self.analyze_plot_dimension()
        
        # 维度3: 世界观
        print("\n🌍 维度3：世界观分析...")
        results['world_dimension'] = self.analyze_world_dimension()
        
        # 维度4: 风格线
        print("\n✍️  维度4：风格分析...")
        results['style_dimension'] = self.analyze_style_dimension()
        
        # 保存综合结果
        output_file = self.output_dir / 'dimensional_analysis_complete.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✨ 多维度分析完成！")
        print(f"💾 结果已保存到: {output_file}")
        
        return results
    
    def analyze_character_dimension(self) -> Dict[str, Any]:
        """
        维度1：角色线分析
        
        策略：
        1. 智能筛选：只保留重要角色（出场>5次）
        2. 关系图谱：构建角色关系网络
        3. 成长轨迹：追踪角色发展
        """
        characters = self.data.get('characters', [])
        
        # 筛选重要角色
        important_chars = [
            char for char in characters 
            if char.get('total_appearances', 0) > 5
        ]
        
        print(f"  原始角色数: {len(characters)}")
        print(f"  重要角色数: {len(important_chars)} (出场>5次)")
        
        # 构建角色关系网络
        relationships = self._extract_relationships(important_chars)
        
        # 分类角色（主角、配角、反派）
        categorized = self._categorize_characters(important_chars)
        
        # 准备给LLM的压缩数据
        compressed_data = {
            'important_characters': [
                {
                    'name': char['name'],
                    'role': char['role'],
                    'appearances': char['total_appearances'],
                    'first_chapter': char['first_appearance_chapter'],
                    'traits': {
                        'appearance': char.get('appearance_traits', [])[:3],
                        'personality': char.get('personality_traits', [])[:3]
                    }
                }
                for char in important_chars[:20]  # 只保留前20个最重要角色
            ],
            'relationships': relationships,
            'categorization': categorized
        }
        
        # 调用LLM生成角色模板
        char_template = self._generate_character_template(compressed_data)
        
        # 保存角色维度分析结果
        result = {
            'total_characters': len(characters),
            'important_characters_count': len(important_chars),
            'compressed_data': compressed_data,
            'character_template': char_template,
            'metadata': {
                'compression_ratio': f"{len(important_chars)}/{len(characters)}",
                'kept_percentage': f"{len(important_chars)/len(characters)*100:.1f}%"
            }
        }
        
        # 保存到文件
        output_file = self.output_dir / 'dimension_1_characters.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        size_kb = output_file.stat().st_size / 1024
        print(f"  ✅ 角色分析完成: {size_kb:.2f} KB")
        print(f"  📊 压缩率: {result['metadata']['compression_ratio']} ({result['metadata']['kept_percentage']})")
        
        return result
    
    def analyze_plot_dimension(self) -> Dict[str, Any]:
        """
        维度2：情节线分析
        
        策略：
        1. 构建情节树：识别主线、支线
        2. 关键转折：提取重要事件（importance=high）
        3. 节奏分析：统计情节密度
        """
        events = self.data.get('events', [])
        plot_arcs = self.data.get('plot_arcs', [])
        
        # 筛选重要事件
        important_events = [
            event for event in events 
            if event.get('importance') in ['high', 'critical']
        ]
        
        print(f"  总事件数: {len(events)}")
        print(f"  重要事件数: {len(important_events)}")
        
        # 按章节范围分段分析（每50章一个里程碑）
        milestones = self._extract_plot_milestones(plot_arcs, important_events, segment_size=50)
        
        # 识别情节类型分布
        plot_types = self._categorize_plot_types(events)
        
        # 准备压缩数据
        compressed_data = {
            'milestones': milestones,
            'important_events': [
                {
                    'chapter': event['chapter_number'],
                    'type': event['type'],
                    'description': event['description'][:100],  # 截断描述
                    'participants': event.get('participants', [])[:5]
                }
                for event in important_events[:30]  # 只保留前30个重要事件
            ],
            'plot_type_distribution': plot_types
        }
        
        # 调用LLM生成情节框架
        plot_framework = self._generate_plot_framework(compressed_data)
        
        result = {
            'total_events': len(events),
            'important_events_count': len(important_events),
            'milestones_count': len(milestones),
            'compressed_data': compressed_data,
            'plot_framework': plot_framework,
            'metadata': {
                'compression_ratio': f"{len(important_events)}/{len(events)}",
                'kept_percentage': f"{len(important_events)/len(events)*100:.1f}%"
            }
        }
        
        # 保存到文件
        output_file = self.output_dir / 'dimension_2_plot.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        size_kb = output_file.stat().st_size / 1024
        print(f"  ✅ 情节分析完成: {size_kb:.2f} KB")
        print(f"  📊 压缩率: {result['metadata']['compression_ratio']} ({result['metadata']['kept_percentage']})")
        
        return result
    
    def analyze_world_dimension(self) -> Dict[str, Any]:
        """
        维度3：世界观分析
        
        策略：
        1. 去重合并：相同元素只保留一个
        2. 按类型分类：力量体系、地理、社会等
        3. 提取核心设定
        """
        world_elements = self.data.get('world_elements', {})
        locations = self.data.get('locations', [])
        
        # 统计各类型元素数量
        element_stats = {
            elem_type: len(elements)
            for elem_type, elements in world_elements.items()
        }
        
        total_elements = sum(element_stats.values())
        print(f"  总世界观元素: {total_elements}")
        print(f"  元素类型数: {len(world_elements)}")
        
        # 智能去重和压缩
        compressed_world = {}
        for elem_type, elements in world_elements.items():
            # 只保留前10个最早出现的元素
            compressed_world[elem_type] = sorted(
                elements, 
                key=lambda x: x.get('first_mentioned_chapter', 999)
            )[:10]
        
        # 主要地点（按出场次数）
        main_locations = sorted(
            locations,
            key=lambda x: len(x.get('appearance_chapters', [])),
            reverse=True
        )[:15]  # 只保留前15个地点
        
        compressed_data = {
            'world_elements_by_type': compressed_world,
            'main_locations': [
                {
                    'name': loc['name'],
                    'type': loc['type'],
                    'first_chapter': loc['first_appearance_chapter'],
                    'appearances': len(loc.get('appearance_chapters', [])),
                    'description': loc.get('descriptions', [{}])[0].get('description', '')[:100]
                }
                for loc in main_locations
            ],
            'element_statistics': element_stats
        }
        
        # 调用LLM生成世界观设定
        world_bible = self._generate_world_bible(compressed_data)
        
        result = {
            'total_elements': total_elements,
            'element_types': len(world_elements),
            'total_locations': len(locations),
            'compressed_data': compressed_data,
            'world_bible': world_bible,
            'metadata': {
                'compression_ratio': f"{sum(len(v) for v in compressed_world.values())}/{total_elements}",
            }
        }
        
        # 保存到文件
        output_file = self.output_dir / 'dimension_3_world.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        size_kb = output_file.stat().st_size / 1024
        print(f"  ✅ 世界观分析完成: {size_kb:.2f} KB")
        
        return result
    
    def analyze_style_dimension(self) -> Dict[str, Any]:
        """
        维度4：风格分析
        
        策略：
        1. 智能采样：不需要所有章节，采样分析即可
        2. 统计特征：叙事视角、情感强度、描写重点
        3. 提取写作模式
        """
        writing_styles = self.data.get('writing_styles', {})
        plot_arcs = self.data.get('plot_arcs', [])
        
        # 采样分析（开头10章 + 每50章采样5章 + 结尾10章）
        sampled_chapters = self._sample_chapters_for_style(plot_arcs)
        
        print(f"  总章节数: {len(plot_arcs)}")
        print(f"  采样章节数: {len(sampled_chapters)}")
        
        # 风格统计
        perspectives = writing_styles.get('narrative_perspectives', {})
        intensities = writing_styles.get('emotional_intensities', {})
        focuses = writing_styles.get('description_focuses', {})
        
        compressed_data = {
            'sampled_chapters': sampled_chapters,
            'narrative_style': {
                'perspectives': perspectives,
                'dominant_perspective': max(perspectives.items(), key=lambda x: x[1])[0] if perspectives else 'unknown'
            },
            'emotional_pattern': {
                'intensities': intensities,
                'average_intensity': self._calculate_avg_intensity(intensities)
            },
            'description_focus': focuses,
            'key_phrases_sample': writing_styles.get('key_phrases', [])[:20]
        }
        
        # 调用LLM生成写作指南
        writing_guide = self._generate_writing_guide(compressed_data)
        
        result = {
            'total_chapters': len(plot_arcs),
            'sampled_chapters_count': len(sampled_chapters),
            'compressed_data': compressed_data,
            'writing_guide': writing_guide,
            'metadata': {
                'sample_ratio': f"{len(sampled_chapters)}/{len(plot_arcs)}",
                'sample_percentage': f"{len(sampled_chapters)/len(plot_arcs)*100:.1f}%"
            }
        }
        
        # 保存到文件
        output_file = self.output_dir / 'dimension_4_style.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        size_kb = output_file.stat().st_size / 1024
        print(f"  ✅ 风格分析完成: {size_kb:.2f} KB")
        print(f"  📊 采样率: {result['metadata']['sample_ratio']} ({result['metadata']['sample_percentage']})")
        
        return result
    
    # ========== 辅助方法 ==========
    
    def _extract_relationships(self, characters: List[Dict]) -> Dict[str, List[str]]:
        """提取角色关系网络"""
        relationships = defaultdict(list)
        
        for char in characters:
            char_name = char['name']
            for rel in char.get('relationships', []):
                if isinstance(rel, dict):
                    target = rel.get('target') or rel.get('with')
                    if target:
                        relationships[char_name].append(target)
        
        return dict(relationships)
    
    def _categorize_characters(self, characters: List[Dict]) -> Dict[str, List[str]]:
        """分类角色"""
        categorized = {
            'protagonist': [],
            'antagonist': [],
            'supporting': [],
            'minor': []
        }
        
        for char in characters:
            role = char.get('role', 'unknown')
            name = char['name']
            
            if 'protagonist' in role.lower() or 'main' in role.lower():
                categorized['protagonist'].append(name)
            elif 'antagonist' in role.lower() or 'villain' in role.lower():
                categorized['antagonist'].append(name)
            elif char.get('total_appearances', 0) > 10:
                categorized['supporting'].append(name)
            else:
                categorized['minor'].append(name)
        
        return categorized
    
    def _extract_plot_milestones(self, plot_arcs: List[Dict], 
                                  important_events: List[Dict],
                                  segment_size: int = 50) -> List[Dict]:
        """提取情节里程碑"""
        total_chapters = len(plot_arcs)
        milestones = []
        
        for i in range(0, total_chapters, segment_size):
            end_chapter = min(i + segment_size, total_chapters)
            
            # 该段的重要事件
            segment_events = [
                e for e in important_events
                if i < e['chapter_number'] <= end_chapter
            ]
            
            if segment_events:
                milestones.append({
                    'chapter_range': f"{i+1}-{end_chapter}",
                    'key_events_count': len(segment_events),
                    'top_events': [e['description'][:50] for e in segment_events[:3]]
                })
        
        return milestones
    
    def _categorize_plot_types(self, events: List[Dict]) -> Dict[str, int]:
        """统计情节类型分布"""
        type_counts = defaultdict(int)
        
        for event in events:
            event_type = event.get('type', 'unknown')
            type_counts[event_type] += 1
        
        return dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _sample_chapters_for_style(self, plot_arcs: List[Dict]) -> List[Dict]:
        """智能采样章节用于风格分析"""
        total = len(plot_arcs)
        sampled = []
        
        # 开头10章
        sampled.extend(plot_arcs[:10])
        
        # 每50章采样5章
        for i in range(10, total - 10, 50):
            sampled.extend(plot_arcs[i:min(i+5, total-10)])
        
        # 结尾10章
        sampled.extend(plot_arcs[-10:])
        
        return [
            {
                'chapter': arc['chapter_number'],
                'title': arc['chapter_title'],
                'word_count': arc['word_count']
            }
            for arc in sampled
        ]
    
    def _calculate_avg_intensity(self, intensities: Dict[str, int]) -> str:
        """计算平均情感强度"""
        intensity_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'very_high': 4
        }
        
        total_score = 0
        total_count = 0
        
        for intensity, count in intensities.items():
            score = intensity_scores.get(intensity.lower(), 2)
            total_score += score * count
            total_count += count
        
        if total_count == 0:
            return 'medium'
        
        avg_score = total_score / total_count
        
        if avg_score < 1.5:
            return 'low'
        elif avg_score < 2.5:
            return 'medium'
        elif avg_score < 3.5:
            return 'high'
        else:
            return 'very_high'
    
    # ========== LLM调用方法（简化版，实际使用时需要完善prompt）==========
    
    def _generate_character_template(self, data: Dict) -> Dict:
        """生成角色模板（简化版）"""
        # TODO: 调用LLM生成角色模板
        # 这里先返回压缩后的数据结构作为demo
        return {
            'template_type': 'character_template',
            'main_characters': data['important_characters'][:5],
            'relationships': data['relationships'],
            'note': '这是简化版demo，实际使用时会调用LLM生成详细模板'
        }
    
    def _generate_plot_framework(self, data: Dict) -> Dict:
        """生成情节框架（简化版）"""
        return {
            'template_type': 'plot_framework',
            'milestones': data['milestones'],
            'key_events': data['important_events'][:10],
            'note': '这是简化版demo，实际使用时会调用LLM生成详细框架'
        }
    
    def _generate_world_bible(self, data: Dict) -> Dict:
        """生成世界观设定（简化版）"""
        return {
            'template_type': 'world_bible',
            'world_elements': data['world_elements_by_type'],
            'main_locations': data['main_locations'][:5],
            'note': '这是简化版demo，实际使用时会调用LLM生成详细设定'
        }
    
    def _generate_writing_guide(self, data: Dict) -> Dict:
        """生成写作指南（简化版）"""
        return {
            'template_type': 'writing_guide',
            'narrative_style': data['narrative_style'],
            'emotional_pattern': data['emotional_pattern'],
            'key_phrases': data['key_phrases_sample'][:10],
            'note': '这是简化版demo，实际使用时会调用LLM生成详细指南'
        }
