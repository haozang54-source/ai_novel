"""
分层存储生成器 - 创建AI友好的多层存储结构
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from .data_aggregator import DataAggregator
from novel_analyzer.utils.smart_chunker import SmartChunker


class LayeredStorageGenerator:
    """分层存储生成器，创建raw/aggregated/chunked/indexes/rag_ready五层结构"""
    
    def __init__(self, novel_name: str, base_output_dir: str, model_type: str = 'gpt4'):
        """
        初始化分层存储生成器
        
        Args:
            novel_name: 小说名称
            base_output_dir: 基础输出目录
            model_type: 目标LLM类型（用于分块大小）
        """
        self.novel_name = novel_name
        self.base_path = Path(base_output_dir) / novel_name
        self.model_type = model_type
        self.chunker = SmartChunker(model_type=model_type)
        
        # 定义各层目录
        self.layers = {
            'raw': self.base_path / 'raw',
            'aggregated': self.base_path / 'aggregated',
            'chunked': self.base_path / 'chunked',
            'indexes': self.base_path / 'indexes',
            'rag_ready': self.base_path / 'rag_ready'
        }
        
        # 创建目录
        for path in self.layers.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def generate_all_layers(self, chapter_summaries_dir: str):
        """
        生成所有层级的存储结构
        
        Args:
            chapter_summaries_dir: 章节摘要目录
        """
        print(f"🏗️  开始生成分层存储结构: {self.novel_name}")
        print(f"📁 输出目录: {self.base_path}")
        print(f"🤖 目标模型: {self.model_type} (最大块: {self.chunker.max_size/1024:.0f}KB)\n")
        
        # 创建聚合器
        aggregator = DataAggregator(chapter_summaries_dir)
        aggregated_data = aggregator.create_aggregated_data()
        
        # Layer 1: Raw - 保存原始完整数据
        print("\n📦 Layer 1: 生成 Raw 层...")
        self._generate_raw_layer(aggregated_data)
        
        # Layer 2: Aggregated - 保存分类聚合数据
        print("\n📊 Layer 2: 生成 Aggregated 层...")
        self._generate_aggregated_layer(aggregated_data)
        
        # Layer 3: Chunked - 生成AI友好分块
        print("\n✂️  Layer 3: 生成 Chunked 层...")
        self._generate_chunked_layer(aggregated_data)
        
        # Layer 4: Indexes - 生成快速索引
        print("\n🗂️  Layer 4: 生成 Indexes 层...")
        self._generate_indexes_layer(aggregated_data)
        
        # Layer 5: RAG Ready - 生成向量检索格式
        print("\n🔍 Layer 5: 生成 RAG Ready 层...")
        self._generate_rag_layer(aggregated_data)
        
        print(f"\n✨ 分层存储生成完成！")
        self._print_storage_summary()
    
    def _generate_raw_layer(self, data: Dict[str, Any]):
        """Layer 1: 原始完整数据（单文件）"""
        raw_file = self.layers['raw'] / f"{self.novel_name}_complete.json"
        
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        size_kb = raw_file.stat().st_size / 1024
        print(f"  ✅ 完整数据: {size_kb:.2f} KB")
    
    def _generate_aggregated_layer(self, data: Dict[str, Any]):
        """Layer 2: 分类聚合数据（按类别分文件）"""
        aggregated_dir = self.layers['aggregated']
        
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
            file_path = aggregated_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            size_kb = file_path.stat().st_size / 1024
            print(f"  ✅ {filename}: {size_kb:.2f} KB")
    
    def _generate_chunked_layer(self, data: Dict[str, Any]):
        """Layer 3: AI友好分块（按大小和语义分块）"""
        chunked_dir = self.layers['chunked']
        
        # Characters - 按角色重要性（出场次数）分块
        self._chunk_and_save(
            data['characters'],
            chunked_dir / 'characters',
            'characters',
            group_by='role'
        )
        
        # Locations - 按地点类型分块
        self._chunk_and_save(
            data['locations'],
            chunked_dir / 'locations',
            'locations',
            group_by='type'
        )
        
        # Events - 按事件类型分块
        self._chunk_and_save(
            data['events'],
            chunked_dir / 'events',
            'events',
            group_by='type'
        )
        
        # World Elements - 已按类型分类，每个类型单独分块
        world_dir = chunked_dir / 'world_elements'
        world_dir.mkdir(parents=True, exist_ok=True)
        
        for elem_type, elements in data['world_elements'].items():
            safe_type = elem_type.replace('/', '_')
            self._chunk_and_save(
                elements,
                world_dir,
                f"{safe_type}",
                group_by=None
            )
        
        # Plot Arcs - 按章节范围分块（每20章一块）
        plot_chunks = self.chunker.chunk_by_chapters(
            data['plot_arcs'],
            chapters_per_chunk=20
        )
        
        plot_dir = chunked_dir / 'plot_arcs'
        plot_dir.mkdir(parents=True, exist_ok=True)
        
        for i, chunk in enumerate(plot_chunks):
            start_ch = chunk[0]['chapter_number']
            end_ch = chunk[-1]['chapter_number']
            file_path = plot_dir / f"chapters_{start_ch:03d}-{end_ch:03d}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
            
            info = self.chunker.get_chunk_info(chunk)
            print(f"  ✅ 第{start_ch}-{end_ch}章: {info['size_kb']} KB, {info['item_count']}章")
    
    def _generate_indexes_layer(self, data: Dict[str, Any]):
        """Layer 4: 快速索引（轻量级查找表）"""
        indexes_dir = self.layers['indexes']
        
        # 角色索引
        char_index = {
            char['name']: {
                'role': char['role'],
                'first_chapter': char['first_appearance_chapter'],
                'total_appearances': char['total_appearances'],
                'appearance_chapters': [c['chapter_number'] for c in char['appearance_chapters']]
            }
            for char in data['characters']
        }
        
        self._save_index(indexes_dir / 'character_index.json', char_index)
        
        # 地点索引
        loc_index = {
            loc['name']: {
                'type': loc['type'],
                'first_chapter': loc['first_appearance_chapter'],
                'appearance_chapters': [c['chapter_number'] for c in loc['appearance_chapters']]
            }
            for loc in data['locations']
        }
        
        self._save_index(indexes_dir / 'location_index.json', loc_index)
        
        # 章节索引
        chapter_index = {
            arc['chapter_number']: {
                'title': arc['chapter_title'],
                'word_count': arc['word_count'],
                'key_points_count': len(arc['key_points'])
            }
            for arc in data['plot_arcs']
        }
        
        self._save_index(indexes_dir / 'chapter_index.json', chapter_index)
        
        # 世界观元素索引
        world_index = {
            elem_type: [e['element'] for e in elements]
            for elem_type, elements in data['world_elements'].items()
        }
        
        self._save_index(indexes_dir / 'world_elements_index.json', world_index)
    
    def _generate_rag_layer(self, data: Dict[str, Any]):
        """Layer 5: RAG检索格式（JSONL格式，每行一个可检索单元）"""
        rag_dir = self.layers['rag_ready']
        
        # Characters RAG
        char_rag_path = rag_dir / 'characters.jsonl'
        with open(char_rag_path, 'w', encoding='utf-8') as f:
            for char in data['characters']:
                rag_item = {
                    'id': f"char_{char['name']}",
                    'type': 'character',
                    'name': char['name'],
                    'content': self._create_character_text(char),
                    'metadata': {
                        'role': char['role'],
                        'first_chapter': char['first_appearance_chapter'],
                        'total_appearances': char['total_appearances']
                    }
                }
                f.write(json.dumps(rag_item, ensure_ascii=False) + '\n')
        
        print(f"  ✅ characters.jsonl: {len(data['characters'])} 条")
        
        # Locations RAG
        loc_rag_path = rag_dir / 'locations.jsonl'
        with open(loc_rag_path, 'w', encoding='utf-8') as f:
            for loc in data['locations']:
                rag_item = {
                    'id': f"loc_{loc['name']}",
                    'type': 'location',
                    'name': loc['name'],
                    'content': self._create_location_text(loc),
                    'metadata': {
                        'type': loc['type'],
                        'first_chapter': loc['first_appearance_chapter']
                    }
                }
                f.write(json.dumps(rag_item, ensure_ascii=False) + '\n')
        
        print(f"  ✅ locations.jsonl: {len(data['locations'])} 条")
        
        # Events RAG
        events_rag_path = rag_dir / 'events.jsonl'
        with open(events_rag_path, 'w', encoding='utf-8') as f:
            for i, event in enumerate(data['events']):
                rag_item = {
                    'id': f"event_{event['chapter_number']}_{i}",
                    'type': 'event',
                    'content': event['description'],
                    'metadata': {
                        'chapter': event['chapter_number'],
                        'event_type': event['type'],
                        'importance': event['importance'],
                        'participants': event['participants']
                    }
                }
                f.write(json.dumps(rag_item, ensure_ascii=False) + '\n')
        
        print(f"  ✅ events.jsonl: {len(data['events'])} 条")
        
        # Plot Arcs RAG
        plot_rag_path = rag_dir / 'plot_arcs.jsonl'
        with open(plot_rag_path, 'w', encoding='utf-8') as f:
            for arc in data['plot_arcs']:
                rag_item = {
                    'id': f"chapter_{arc['chapter_number']}",
                    'type': 'plot_arc',
                    'content': self._create_plot_text(arc),
                    'metadata': {
                        'chapter': arc['chapter_number'],
                        'title': arc['chapter_title'],
                        'word_count': arc['word_count']
                    }
                }
                f.write(json.dumps(rag_item, ensure_ascii=False) + '\n')
        
        print(f"  ✅ plot_arcs.jsonl: {len(data['plot_arcs'])} 条")
    
    def _chunk_and_save(self, items: List[Dict], output_dir: Path, 
                        category: str, group_by: Optional[str] = None):
        """分块并保存数据"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        chunks = self.chunker.chunk_by_items(items, group_key=group_by)
        
        for i, chunk in enumerate(chunks):
            file_path = output_dir / f"{category}_part_{i+1:02d}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
            
            info = self.chunker.get_chunk_info(chunk)
            print(f"  ✅ {category}_part_{i+1:02d}: {info['size_kb']} KB, {info['item_count']}项, {info['utilization']:.1f}%利用率")
    
    def _save_index(self, file_path: Path, index_data: Dict):
        """保存索引文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        size_kb = file_path.stat().st_size / 1024
        print(f"  ✅ {file_path.name}: {size_kb:.2f} KB")
    
    def _create_character_text(self, char: Dict) -> str:
        """为角色创建RAG检索文本"""
        parts = [
            f"角色名称：{char['name']}",
            f"角色定位：{char['role']}",
            f"首次出场：第{char['first_appearance_chapter']}章",
            f"总出场次数：{char['total_appearances']}次"
        ]
        
        if char.get('appearance_traits'):
            parts.append(f"外貌特征：{', '.join(char['appearance_traits'])}")
        
        if char.get('personality_traits'):
            parts.append(f"性格特征：{', '.join(char['personality_traits'])}")
        
        if char.get('status_changes'):
            changes = [f"第{s['chapter']}章：{s['change']}" for s in char['status_changes'][:5]]
            parts.append(f"关键转变：{'; '.join(changes)}")
        
        return '\n'.join(parts)
    
    def _create_location_text(self, loc: Dict) -> str:
        """为地点创建RAG检索文本"""
        parts = [
            f"地点名称：{loc['name']}",
            f"地点类型：{loc['type']}",
            f"首次出现：第{loc['first_appearance_chapter']}章"
        ]
        
        if loc.get('descriptions'):
            desc = loc['descriptions'][0]['description']
            parts.append(f"描述：{desc}")
        
        return '\n'.join(parts)
    
    def _create_plot_text(self, arc: Dict) -> str:
        """为情节创建RAG检索文本"""
        parts = [
            f"章节：第{arc['chapter_number']}章 {arc['chapter_title']}",
            f"主要内容：{arc['main_content']}"
        ]
        
        if arc.get('key_points'):
            parts.append(f"关键要点：{'; '.join(arc['key_points'])}")
        
        if arc.get('chapter_purpose'):
            parts.append(f"章节作用：{arc['chapter_purpose']}")
        
        return '\n'.join(parts)
    
    def _print_storage_summary(self):
        """打印存储结构摘要"""
        print("\n" + "="*60)
        print("📊 存储结构摘要")
        print("="*60)
        
        for layer_name, layer_path in self.layers.items():
            total_size = sum(f.stat().st_size for f in layer_path.rglob('*') if f.is_file())
            file_count = len(list(layer_path.rglob('*.json*')))
            
            print(f"\n{layer_name.upper()} 层:")
            print(f"  📁 路径: {layer_path}")
            print(f"  📄 文件数: {file_count}")
            print(f"  💾 总大小: {total_size/1024:.2f} KB")
        
        print("\n" + "="*60)
