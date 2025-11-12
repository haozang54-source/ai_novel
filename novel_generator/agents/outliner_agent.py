"""大纲师智能体 - 负责生成故事大纲"""
from typing import Dict, Any, List
from .base_agent import BaseAgent


class OutlinerAgent(BaseAgent):
    """大纲师 - 生成详细的章节大纲"""
    
    def __init__(self, llm=None):
        super().__init__(llm, "Outliner")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成故事大纲"""
        self.log("📝 开始生成故事大纲...")

        story_concept = input_data.get("story_concept", "未指定")
        genre = input_data.get("genre", "玄幻")
        outline_level = input_data.get("outline_level", "chapter")
        story_rhythm = input_data.get("story_rhythm", "起承转合")
        key_points = input_data.get("key_points", [])

        key_points_text = "\n".join([
            f"{idx + 1}. {point}" for idx, point in enumerate(key_points)
        ]) if key_points else "1. 自由发挥并确保节奏紧凑"

        if outline_level == "volume":
            target_volumes = input_data.get("target_volumes")
            if not target_volumes:
                estimated = input_data.get("target_chapters", 12)
                target_volumes = max(3, estimated // 12)

            outline_prompt = f"""
你是一位结构规划大师,需要为长篇小说设计统领全局的卷级大纲。

故事信息:
- 核心概念: {story_concept}
- 小说类型: {genre}
- 期望卷数: {target_volumes} 卷
- 整体节奏: {story_rhythm}
- 关键创作要点:\n{key_points_text}

输出要求:
1. 每一卷必须承担清晰的剧情使命,推动主线或人物成长
2. 卷与卷之间要形成递进关系,铺垫、爆发、收束层层推进
3. 兼顾情绪节奏,注明每卷的情感基调
4. 指出核心冲突或矛盾焦点

请按如下格式输出,严格保留标头,方便解析:
第X卷: [卷名]
定位: [该卷在全书中的功能定位]
篇幅: [覆盖的章节范围或篇幅比例]
核心任务:
- [任务A]
- [任务B]
关键转折:
- [转折A]
- [转折B]
核心冲突: [主要矛盾]
情感基调: [情绪氛围]
主要人物成长: [角色发展要点]

---
"""
            self.log(f"🎯 正在规划 {target_volumes} 卷的宏观结构...")
            response = self.invoke_llm(outline_prompt)
            outline = self._parse_volume_outline(response, target_volumes)
            unit_label = "卷"
        else:
            target_chapters = input_data.get("target_chapters", 6)
            outline_prompt = f"""
你是一位专业的小说大纲师,擅长构建引人入胜的章节框架。

故事信息:
- 核心概念: {story_concept}
- 小说类型: {genre}
- 章节数量: {target_chapters} 章
- 整体节奏: {story_rhythm}
- 关键创作要点:\n{key_points_text}

要求:
1. 每章都要有明确的冲突和看点
2. 整体结构符合{genre}小说的特点,节奏张弛有度
3. 每章之间要有清晰的承接关系

请为每一章生成:
- 章节标题 (吸引眼球)
- 章节摘要 (100字左右)
- 关键事件 (2-3个)
- 主要冲突
- 情感节拍 (紧张/舒缓/悬疑等)

严格按照以下格式输出,方便解析:
第X章: [标题]
摘要: [章节摘要]
关键事件:
- [事件1]
- [事件2]
冲突: [主要冲突]
情感: [情感节拍]

---
"""
            self.log(f"🎯 正在为 {target_chapters} 章节规划大纲...")
            response = self.invoke_llm(outline_prompt)
            outline = self._parse_outline(response, target_chapters)
            unit_label = "章"

        self.log(f"✅ 大纲生成完成,共 {len(outline)} {unit_label}")
        for item in outline:
            self.log(f"   第{item['chapter_num']}{unit_label}: {item['title']}")

        return {
            "outline": outline,
            "raw_outline": response,
            "outline_level": outline_level
        }

    def _parse_outline(self, outline_text: str, expected_chapters: int) -> List[Dict[str, Any]]:
        chapters: List[Dict[str, Any]] = []
        current_chapter: Dict[str, Any] | None = None

        for raw_line in outline_text.split('\n'):
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith('第') and '章' in line and ':' in line:
                if current_chapter:
                    chapters.append(current_chapter)

                parts = line.split(':', 1)
                chapter_num = len(chapters) + 1
                title = parts[1].strip() if len(parts) > 1 else f"第{chapter_num}章"

                current_chapter = {
                    "chapter_num": chapter_num,
                    "title": title,
                    "summary": "",
                    "key_events": [],
                    "conflicts": "",
                    "emotional_beat": ""
                }
                continue

            if not current_chapter:
                continue

            if line.startswith('摘要:'):
                current_chapter['summary'] = line.replace('摘要:', '').strip()
            elif line.startswith('关键事件:'):
                continue
            elif line.startswith('- '):
                current_chapter['key_events'].append(line[2:].strip())
            elif line.startswith('冲突:'):
                current_chapter['conflicts'] = line.replace('冲突:', '').strip()
            elif line.startswith('情感:'):
                current_chapter['emotional_beat'] = line.replace('情感:', '').strip()

        if current_chapter:
            chapters.append(current_chapter)

        if len(chapters) == 0:
            self.log("⚠️ 大纲解析失败,生成默认章节结构")
            for i in range(expected_chapters):
                chapters.append({
                    "chapter_num": i + 1,
                    "title": f"第{i + 1}章",
                    "summary": "章节内容待生成",
                    "key_events": ["主要事件"],
                    "conflicts": "待定",
                    "emotional_beat": "正常"
                })

        return chapters

    def _parse_volume_outline(self, outline_text: str, expected_volumes: int) -> List[Dict[str, Any]]:
        volumes: List[Dict[str, Any]] = []
        current_volume: Dict[str, Any] | None = None

        sections = {
            '定位:': 'positioning',
            '篇幅:': 'length',
            '核心任务:': 'core_tasks',
            '关键任务:': 'core_tasks',
            '关键转折:': 'key_turns',
            '核心冲突:': 'conflicts',
            '情感基调:': 'emotional_beat',
            '主要人物成长:': 'character_growth'
        }

        active_list_key: str | None = None

        for raw_line in outline_text.split('\n'):
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith('第') and '卷' in line and ':' in line:
                if current_volume:
                    volumes.append(self._finalize_volume(current_volume))

                parts = line.split(':', 1)
                volume_num = len(volumes) + 1
                title = parts[1].strip() if len(parts) > 1 else f"第{volume_num}卷"

                current_volume = {
                    "chapter_num": volume_num,
                    "title": title,
                    "summary": "",
                    "key_events": [],
                    "conflicts": "",
                    "emotional_beat": "",
                    "positioning": "",
                    "length": "",
                    "character_growth": "",
                    "core_tasks": [],
                    "key_turns": []
                }
                active_list_key = None
                continue

            if not current_volume:
                continue

            matched_section = next((label for label in sections if line.startswith(label)), None)
            if matched_section:
                key = sections[matched_section]
                content = line.replace(matched_section, '').strip()
                if key in ['core_tasks', 'key_turns']:
                    current_volume[key] = []
                    active_list_key = key
                    if content:
                        current_volume[key].append(content)
                else:
                    current_volume[key] = content
                    active_list_key = None
                continue

            if line.startswith('- '):
                if active_list_key and isinstance(current_volume.get(active_list_key), list):
                    current_volume[active_list_key].append(line[2:].strip())
                continue

        if current_volume:
            volumes.append(self._finalize_volume(current_volume))

        if len(volumes) == 0:
            self.log("⚠️ 卷级大纲解析失败,生成默认结构")
            for i in range(expected_volumes):
                volumes.append({
                    "chapter_num": i + 1,
                    "title": f"第{i + 1}卷",
                    "summary": "本卷负责推进主线,安排关键冲突与人物成长。",
                    "key_events": ["推进主线", "制造冲突"],
                    "conflicts": "主要矛盾待定",
                    "emotional_beat": "情感基调待定"
                })

        return volumes

    def _finalize_volume(self, volume: Dict[str, Any]) -> Dict[str, Any]:
        summary_parts: List[str] = []
        if volume.get('positioning'):
            summary_parts.append(f"定位: {volume['positioning']}")
        if volume.get('length'):
            summary_parts.append(f"篇幅: {volume['length']}")
        if volume.get('character_growth'):
            summary_parts.append(f"人物成长: {volume['character_growth']}")

        volume['summary'] = '\n'.join(summary_parts) if summary_parts else volume.get('summary', '')

        key_events: List[str] = []
        for field in ['core_tasks', 'key_turns']:
            items = volume.get(field)
            if isinstance(items, list):
                key_events.extend(items)
        volume['key_events'] = key_events

        if not volume.get('conflicts'):
            volume['conflicts'] = volume.get('positioning', '')

        if not volume.get('emotional_beat'):
            volume['emotional_beat'] = '节奏平衡'

        return {
            'chapter_num': volume.get('chapter_num', len(key_events) + 1),
            'title': volume.get('title', '阶段大纲'),
            'summary': volume.get('summary', ''),
            'key_events': volume.get('key_events', []),
            'conflicts': volume.get('conflicts', ''),
            'emotional_beat': volume.get('emotional_beat', '')
        }
