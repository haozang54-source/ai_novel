"""
修复工具 - 使用LLM重新生成缺失的字段
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# 导入LLM相关包
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI

from utils.file_utils import FileUtils
from utils.json_parser import JSONParser


class MissingFieldsRegenerator:
    """使用LLM重新生成缺失字段的修复器"""
    
    REQUIRED_FIELDS = [
        'characters',
        'locations', 
        'events',
        'world_elements',
        'writing_style_notes',
        'chapter_summary'
    ]
    
    def __init__(self, llm, retry_times: int = 5):
        """
        初始化修复器
        
        Args:
            llm: LangChain LLM实例
            retry_times: 每个字段的重试次数
        """
        self.llm = llm
        self.retry_times = retry_times
    
    def scan_incomplete_chapters(self, summaries_dir: str) -> Dict[int, List[str]]:
        """
        扫描不完整的章节
        
        Args:
            summaries_dir: chapter_summaries目录路径
            
        Returns:
            {chapter_number: [missing_fields]}
        """
        summaries_path = Path(summaries_dir)
        incomplete_chapters = {}
        
        for json_file in sorted(summaries_path.glob("chapter_*.json")):
            try:
                chapter_num = int(json_file.stem.split('_')[1])
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                missing_fields = [
                    field for field in self.REQUIRED_FIELDS 
                    if field not in data
                ]
                
                if missing_fields:
                    incomplete_chapters[chapter_num] = missing_fields
                    
            except Exception as e:
                print(f"⚠️  读取 {json_file.name} 失败: {e}")
        
        return incomplete_chapters
    
    def load_chapter_content(self, chapter_num: int, novel_dir: str) -> Optional[str]:
        """
        加载章节原始内容
        
        Args:
            chapter_num: 章节编号
            novel_dir: 小说文件夹路径
            
        Returns:
            章节内容文本
        """
        novel_path = Path(novel_dir)
        
        # 尝试常见的文件名格式
        patterns = [
            f"第{chapter_num}章*.txt",
            f"第{chapter_num:03d}章*.txt",
            f"chapter_{chapter_num:03d}.txt",
            f"{chapter_num:03d}*.txt"
        ]
        
        for pattern in patterns:
            files = list(novel_path.glob(pattern))
            if files:
                try:
                    with open(files[0], 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    # 智能截断
                    max_length = 6000
                    if len(content) > max_length:
                        truncate_pos = max_length
                        for i in range(max_length, max(0, max_length - 200), -1):
                            if content[i] in '。！？…\n':
                                truncate_pos = i + 1
                                break
                        content = content[:truncate_pos]
                    
                    return content
                except Exception as e:
                    print(f"      ❌ 读取文件失败: {e}")
        
        return None
    
    def regenerate_field(self, field_name: str, content: str, chapter_num: int) -> Optional[any]:
        """
        使用LLM重新生成单个字段
        
        Args:
            field_name: 字段名称
            content: 章节内容
            chapter_num: 章节编号
            
        Returns:
            生成的字段数据
        """
        for attempt in range(self.retry_times):
            try:
                if field_name == 'characters':
                    result = self._extract_characters(content)
                elif field_name == 'locations':
                    result = self._extract_locations(content)
                elif field_name == 'events':
                    result = self._extract_events(content)
                elif field_name == 'world_elements':
                    result = self._extract_world_elements(content)
                elif field_name == 'writing_style_notes':
                    result = self._extract_writing_style(content)
                elif field_name == 'chapter_summary':
                    result = self._extract_chapter_summary(content)
                else:
                    return None
                
                if result is not None:
                    return result
                    
            except Exception as e:
                if attempt < self.retry_times - 1:
                    print(f"        ⚠️  重试 {attempt + 1}/{self.retry_times}: {e}")
                    time.sleep(2)
                else:
                    print(f"        ❌ 达到最大重试次数: {e}")
        
        return None
    
    def _extract_characters(self, content: str) -> Optional[List]:
        """提取角色信息"""
        prompt = f"""分析以下章节内容，只提取角色信息。

章节内容：
{content}

请严格按照以下JSON格式输出角色列表，不要添加其他文字：
[
  {{
    "name": "角色名",
    "role": "protagonist/antagonist/supporting",
    "first_appearance": true,
    "status_changes": ["变化描述"],
    "relationships": [
      {{
        "target": "相关角色名",
        "relation_type": "丈夫/妻子/父亲/母亲/兄弟/姐妹/师徒/朋友/敌人/恋人等",
        "description": "关系描述"
      }}
    ],
    "appearance_traits": ["外貌特征"],
    "personality_traits": ["性格特征"]
  }}
]

只输出JSON数组，不要其他文字。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_locations(self, content: str) -> Optional[List]:
        """提取地点信息"""
        prompt = f"""分析以下章节内容，只提取地点信息。

章节内容：
{content}

请严格按照以下JSON格式输出地点列表：
[
  {{
    "name": "地点名称",
    "type": "城市/村落/山脉/宗门/秘境/其他",
    "description": "地点描述",
    "importance": "high/medium/low"
  }}
]

只输出JSON数组。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_events(self, content: str) -> Optional[List]:
        """提取事件信息"""
        prompt = f"""分析以下章节内容，只提取关键事件。

章节内容：
{content}

请严格按照以下JSON格式输出事件列表：
[
  {{
    "event_type": "战斗/修炼/探索/社交/阴谋/其他",
    "description": "事件描述",
    "participants": ["参与者1", "参与者2"],
    "location": "发生地点",
    "outcome": "事件结果"
  }}
]

只输出JSON数组。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_world_elements(self, content: str) -> Optional[Dict]:
        """提取世界观元素"""
        prompt = f"""分析以下章节内容，提取世界观元素。

章节内容：
{content}

请严格按照以下JSON格式输出：
{{
  "cultivation_system": ["修炼体系相关"],
  "magic_items": ["法宝、灵药等"],
  "organizations": ["门派、势力等"],
  "rules_laws": ["世界规则、天道等"],
  "other": ["其他世界观元素"]
}}

只输出JSON对象。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_writing_style(self, content: str) -> Optional[Dict]:
        """提取写作风格"""
        prompt = f"""分析以下章节的写作风格。

章节内容：
{content}

请严格按照以下JSON格式输出：
{{
  "narrative_techniques": ["叙事技巧"],
  "language_features": ["语言特点"],
  "pacing_notes": "节奏控制说明",
  "emotional_tone": "情感基调",
  "notable_phrases": ["金句、特色表达"]
}}

只输出JSON对象。"""
        
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        return JSONParser.parse(response_text)
    
    def _extract_chapter_summary(self, content: str) -> Optional[str]:
        """提取章节摘要"""
        prompt = f"""用1-2句话概括以下章节的核心内容。

章节内容：
{content}

只输出概括文字，不要其他内容。"""
        
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def repair_chapter(
        self, 
        chapter_num: int, 
        missing_fields: List[str],
        summaries_dir: str,
        novel_dir: str
    ) -> bool:
        """
        修复单个章节的缺失字段
        
        Args:
            chapter_num: 章节编号
            missing_fields: 缺失的字段列表
            summaries_dir: chapter_summaries目录
            novel_dir: 小说原始文件目录
            
        Returns:
            是否修复成功
        """
        print(f"\n📄 修复章节 {chapter_num}")
        print(f"   缺失字段: {', '.join(missing_fields)}")
        
        # 加载章节内容
        print(f"   ⏳ 加载章节内容...")
        content = self.load_chapter_content(chapter_num, novel_dir)
        
        if not content:
            print(f"   ❌ 无法找到章节 {chapter_num} 的原始文件")
            return False
        
        # 加载现有数据
        summary_file = Path(summaries_dir) / f"chapter_{chapter_num:03d}.json"
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"   ❌ 读取现有数据失败: {e}")
            return False
        
        # 逐个重新生成缺失字段
        success_count = 0
        for field in missing_fields:
            print(f"   → 生成 {field}...")
            
            result = self.regenerate_field(field, content, chapter_num)
            
            if result is not None:
                data[field] = result
                print(f"      ✓ 成功")
                success_count += 1
            else:
                print(f"      ✗ 失败")
            
            time.sleep(1)  # 避免请求过快
        
        # 保存更新后的数据
        if success_count > 0:
            try:
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"   ✅ 成功修复 {success_count}/{len(missing_fields)} 个字段")
                return success_count == len(missing_fields)
            except Exception as e:
                print(f"   ❌ 保存失败: {e}")
                return False
        else:
            print(f"   ❌ 所有字段重新生成均失败")
            return False


def init_llm(config: dict):
    """
    初始化LLM（从main.py复制）
    
    Args:
        config: 配置字典
        
    Returns:
        LLM实例
    """
    llm_config = config.get('llm', {})
    
    # 从环境变量读取配置（优先级高于config.yaml）
    provider = os.getenv('LLM_PROVIDER', llm_config.get('provider', 'ollama'))
    temperature = float(os.getenv('LLM_TEMPERATURE', llm_config.get('temperature', 0.3)))
    max_tokens = int(os.getenv('LLM_MAX_TOKENS', llm_config.get('max_tokens', 3000)))
    
    if provider == 'ollama':
        model = os.getenv('OLLAMA_MODEL', llm_config.get('model', 'qwen2.5:7b-instruct'))
        base_url = os.getenv('OLLAMA_BASE_URL', llm_config.get('base_url', 'http://localhost:11434'))
        
        llm = OllamaLLM(
            model=model,
            base_url=base_url,
            temperature=temperature,
        )
        print(f"✓ 使用 Ollama 模型: {model}")
    
    elif provider == 'openai':
        model = os.getenv('OPENAI_MODEL', llm_config.get('model', 'gpt-3.5-turbo'))
        base_url = os.getenv('OPENAI_API_BASE', llm_config.get('base_url'))
        api_key = os.getenv('OPENAI_API_KEY', llm_config.get('api_key', 'dummy'))
        
        llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        print(f"✓ 使用 OpenAI 兼容接口: {model}")
    
    else:
        raise ValueError(f"不支持的LLM provider: {provider}")
    
    return llm


def main():
    parser = argparse.ArgumentParser(description='使用LLM重新生成缺失字段')
    parser.add_argument('--summaries-dir', required=True, help='chapter_summaries目录路径')
    parser.add_argument('--novel-dir', required=True, help='小说原始文件目录路径')
    parser.add_argument('--config', help='配置文件路径（可选）')
    parser.add_argument('--report-only', action='store_true', help='只生成报告，不执行修复')
    parser.add_argument('--auto-confirm', action='store_true', help='自动确认，不询问')
    
    args = parser.parse_args()
    
    # 加载环境变量（从项目根目录）
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()  # 尝试从当前目录加载
    
    # 加载配置
    if args.config:
        import yaml
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        import yaml
        default_config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config', 
            'config.yaml'
        )
        with open(default_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    
    # 初始化LLM
    llm = init_llm(config)
    
    # 创建修复器
    regenerator = MissingFieldsRegenerator(llm)
    
    # 扫描不完整章节
    print("🔍 扫描不完整章节...\n")
    incomplete_chapters = regenerator.scan_incomplete_chapters(args.summaries_dir)
    
    if not incomplete_chapters:
        print("✅ 所有章节数据完整！")
        return
    
    # 显示报告
    print("=" * 80)
    print(f"📊 发现 {len(incomplete_chapters)} 个不完整章节\n")
    
    for chapter_num in sorted(incomplete_chapters.keys()):
        missing_fields = incomplete_chapters[chapter_num]
        print(f"  📄 章节 {chapter_num:03d}")
        print(f"     缺失字段 ({len(missing_fields)}): {', '.join(missing_fields)}")
    
    print("=" * 80)
    
    # 如果只是生成报告
    if args.report_only:
        report_file = os.path.join(args.summaries_dir, 'incomplete_chapters_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_incomplete': len(incomplete_chapters),
                'chapters': {
                    str(ch): fields for ch, fields in incomplete_chapters.items()
                }
            }, f, ensure_ascii=False, indent=2)
        print(f"\n📝 报告已保存到: {report_file}")
        return
    
    # 确认修复
    if not args.auto_confirm:
        response = input(f"\n是否开始使用LLM重新生成这 {len(incomplete_chapters)} 个章节的缺失字段？(y/n): ")
        if response.lower() != 'y':
            print("❌ 已取消")
            return
    
    # 执行修复
    print("\n" + "=" * 80)
    print("🔧 开始修复...\n")
    
    success_count = 0
    failed_chapters = []
    
    for chapter_num in sorted(incomplete_chapters.keys()):
        missing_fields = incomplete_chapters[chapter_num]
        
        success = regenerator.repair_chapter(
            chapter_num,
            missing_fields,
            args.summaries_dir,
            args.novel_dir
        )
        
        if success:
            success_count += 1
        else:
            failed_chapters.append(chapter_num)
    
    # 修复总结
    print("\n" + "=" * 80)
    print("📊 修复完成！\n")
    print(f"  ✅ 成功修复: {success_count}/{len(incomplete_chapters)} 个章节")
    
    if failed_chapters:
        print(f"  ❌ 修复失败: {len(failed_chapters)} 个章节")
        print(f"     章节编号: {failed_chapters}")
    
    print("=" * 80)


if __name__ == '__main__':
    main()
