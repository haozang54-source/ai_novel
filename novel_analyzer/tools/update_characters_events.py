"""
更新已有章节分析结果中的人物和事件信息

使用分步骤提取方法重新生成 characters 和 events 字段
"""
import os
import sys
import json
import time
import argparse
from typing import Dict, Optional, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.json_parser import JSONParser

# 导入LLM
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI


class CharacterEventUpdater:
    """人物和事件信息更新器"""
    
    def __init__(self, llm):
        """
        初始化更新器
        
        Args:
            llm: LangChain LLM实例
        """
        self.llm = llm
    
    def update_chapter_file(self, json_file: str, novel_dir: str, backup: bool = True) -> bool:
        """
        更新单个章节JSON文件
        
        Args:
            json_file: 章节JSON文件路径
            novel_dir: 小说原文目录
            backup: 是否备份原文件
            
        Returns:
            是否成功
        """
        try:
            # 读取现有JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chapter_number = data.get('chapter_number')
            chapter_title = data.get('chapter_title', '')
            
            if chapter_number is None:
                print(f"  ⚠️  文件缺少 chapter_number 字段")
                return False
            
            # 读取章节原文（优先使用标题匹配）
            chapter_content = self._load_chapter_content(novel_dir, chapter_number, chapter_title)
            if not chapter_content:
                print(f"  ⚠️  无法读取章节 {chapter_number} ({chapter_title}) 的原文")
                return False
            
            # 备份原文件
            if backup:
                backup_file = json_file + '.backup'
                if not os.path.exists(backup_file):
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"  💾 已备份到: {os.path.basename(backup_file)}")
            
            # 更新 characters
            print(f"  🔄 更新 characters...", end='', flush=True)
            new_characters = self._extract_characters(chapter_content)
            if new_characters is not None:
                data['characters'] = new_characters
                print(f" ✓ 成功 (共{len(new_characters)}个角色)")
            else:
                print(f" ✗ 失败，保留原数据")
            
            time.sleep(0.5)
            
            # 更新 events
            print(f"  🔄 更新 events...", end='', flush=True)
            new_events = self._extract_events(chapter_content)
            if new_events is not None:
                data['events'] = new_events
                print(f" ✓ 成功 (共{len(new_events)}个事件)")
            else:
                print(f" ✗ 失败，保留原数据")
            
            # 保存更新后的文件
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"  ❌ 更新失败: {e}")
            return False
    
    def _load_chapter_content(self, novel_dir: str, chapter_number: int, chapter_title: str = '') -> Optional[str]:
        """
        加载章节原文
        
        Args:
            novel_dir: 小说目录
            chapter_number: 章节号
            chapter_title: 章节标题（可选，用于精确匹配）
            
        Returns:
            章节内容
        """
        # 方法1: 如果有章节标题，直接匹配标题
        if chapter_title:
            title_file = os.path.join(novel_dir, f"{chapter_title}.txt")
            if os.path.exists(title_file):
                try:
                    with open(title_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content = self._truncate_content(content)
                    print(f"  📖 加载文件: {chapter_title}.txt")
                    return content
                except Exception as e:
                    print(f"  ⚠️  读取文件 {chapter_title}.txt 失败: {e}")
        
        # 方法2: 遍历目录查找包含章节号的文件
        try:
            for filename in os.listdir(novel_dir):
                if not filename.endswith('.txt'):
                    continue
                
                # 匹配 "第X章" 开头的文件
                if filename.startswith(f"第{chapter_number}章"):
                    file_path = os.path.join(novel_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        content = self._truncate_content(content)
                        print(f"  📖 加载文件: {filename}")
                        return content
                    except Exception as e:
                        print(f"  ⚠️  读取文件 {filename} 失败: {e}")
        except Exception as e:
            print(f"  ⚠️  遍历目录失败: {e}")
        
        # 方法3: 尝试固定格式的文件名
        possible_names = [
            f"第{chapter_number}章.txt",
            f"第{chapter_number:03d}章.txt",
            f"第{chapter_number:04d}章.txt",
            f"{chapter_number}.txt",
            f"{chapter_number:03d}.txt",
            f"chapter_{chapter_number}.txt",
            f"chapter_{chapter_number:03d}.txt",
        ]
        
        for name in possible_names:
            file_path = os.path.join(novel_dir, name)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content = self._truncate_content(content)
                    print(f"  📖 加载文件: {name}")
                    return content
                except Exception as e:
                    print(f"  ⚠️  读取文件 {name} 失败: {e}")
        
        return None
    
    def _truncate_content(self, content: str) -> str:
        """
        智能截断内容
        
        Args:
            content: 原始内容
            
        Returns:
            截断后的内容
        """
        max_length = 6000
        if len(content) > max_length:
            truncate_pos = max_length
            for i in range(max_length, max(0, max_length - 200), -1):
                if content[i] in '。！？…\n':
                    truncate_pos = i + 1
                    break
            content = content[:truncate_pos]
        return content
    
    def _extract_characters(self, content: str) -> Optional[List]:
        """
        提取角色信息（分步骤执行）
        
        步骤1: 获取角色名单
        步骤2: 逐个分析角色详情
        步骤3: 整合结果
        """
        try:
            # ===== 步骤1: 获取角色名单 =====
            step1_prompt = f"""阅读以下章节内容，列出本章出现的所有角色名字。

章节内容：
{content}

要求：
1. 只输出角色名字列表，用JSON数组格式
2. 不要包含任何解释或额外信息
3. 格式：["角色1", "角色2", "角色3"]

角色名单："""
            
            response = self.llm.invoke(step1_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            character_names = JSONParser.parse(response_text)
            
            if not character_names or not isinstance(character_names, list):
                return None
            
            # ===== 步骤2: 逐个分析角色 =====
            characters = []
            for idx, name in enumerate(character_names[:10], 1):  # 最多分析10个角色
                print(f"\n      → 分析角色 {idx}/{min(len(character_names), 10)}: {name}...", end='', flush=True)
                
                step2_prompt = f"""分析章节中角色"{name}"的信息。

章节内容：
{content}

请只输出该角色的JSON对象，格式如下：
{{
  "name": "{name}",
  "role": "protagonist/antagonist/supporting",
  "first_appearance": true/false,
  "status_changes": ["状态变化描述"],
  "relationships": [
    {{
      "target": "相关角色名",
      "relation_type": "关系类型",
      "description": "关系描述"
    }}
  ],
  "appearance_traits": ["外貌特征"],
  "personality_traits": ["性格特征"]
}}

只输出JSON对象："""
                
                char_response = self.llm.invoke(step2_prompt)
                char_text = char_response.content if hasattr(char_response, 'content') else str(char_response)
                char_data = JSONParser.parse(char_text)
                
                if char_data and isinstance(char_data, dict):
                    char_data['name'] = name
                    characters.append(char_data)
                    print(f" ✓")
                else:
                    # 如果解析失败，创建基本信息
                    characters.append({
                        "name": name,
                        "role": "supporting",
                        "first_appearance": False,
                        "status_changes": [],
                        "relationships": [],
                        "appearance_traits": [],
                        "personality_traits": []
                    })
                    print(f" ⚠️  (使用默认)")
                
                time.sleep(0.3)  # 避免请求过快
            
            return characters if characters else []
            
        except Exception as e:
            print(f"\n      ❌ 角色提取异常: {str(e)[:100]}")
            return None
    
    def _extract_events(self, content: str) -> Optional[List]:
        """
        提取事件信息（分步骤执行）
        
        步骤1: 获取事件概要列表
        步骤2: 逐个分析事件详情
        """
        try:
            # ===== 步骤1: 获取事件列表 =====
            step1_prompt = f"""阅读以下章节内容，列出本章发生的关键事件（3-5个）。

章节内容：
{content}

要求：
1. 只输出事件描述列表，用JSON数组格式
2. 每个事件用一句话简要概括
3. 格式：["事件1描述", "事件2描述", "事件3描述"]

事件列表："""
            
            response = self.llm.invoke(step1_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            event_descriptions = JSONParser.parse(response_text)
            
            if not event_descriptions or not isinstance(event_descriptions, list):
                return None
            
            # ===== 步骤2: 逐个分析事件详情 =====
            events = []
            for idx, desc in enumerate(event_descriptions[:5], 1):  # 最多分析5个事件
                print(f"\n      → 分析事件 {idx}/{min(len(event_descriptions), 5)}: {desc[:30]}...", end='', flush=True)
                
                step2_prompt = f"""分析该事件的详细信息："{desc}"

章节内容：
{content}

请只输出该事件的JSON对象：
{{
  "type": "conflict/development/climax/turning_point",
  "description": "{desc}",
  "importance": "high/medium/low",
  "emotional_tone": "情感基调",
  "participants": ["参与角色1", "参与角色2"]
}}

只输出JSON对象："""
                
                event_response = self.llm.invoke(step2_prompt)
                event_text = event_response.content if hasattr(event_response, 'content') else str(event_response)
                event_data = JSONParser.parse(event_text)
                
                if event_data and isinstance(event_data, dict):
                    event_data['description'] = desc  # 确保描述正确
                    events.append(event_data)
                    print(f" ✓")
                else:
                    # 解析失败时创建基本事件
                    events.append({
                        "type": "development",
                        "description": desc,
                        "importance": "medium",
                        "emotional_tone": "平静",
                        "participants": []
                    })
                    print(f" ⚠️  (使用默认)")
                
                time.sleep(0.3)  # 避免请求过快
            
            return events if events else []
            
        except Exception as e:
            print(f"\n      ❌ 事件提取异常: {str(e)[:100]}")
            return None


def init_llm():
    """初始化LLM"""
    provider = os.getenv('LLM_PROVIDER', 'ollama')
    
    if provider == 'ollama':
        model = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b-instruct')
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        llm = OllamaLLM(
            model=model,
            base_url=base_url,
            temperature=0.3,
            timeout=120,
        )
        print(f"✓ 使用 Ollama 模型: {model}")
    
    elif provider == 'openai':
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        base_url = os.getenv('OPENAI_API_BASE')
        api_key = os.getenv('OPENAI_API_KEY', 'dummy')
        
        llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=0.3,
            max_tokens=3000,
            request_timeout=120,
        )
        print(f"✓ 使用 OpenAI 兼容接口: {model}")
    
    else:
        raise ValueError(f"不支持的LLM provider: {provider}")
    
    return llm


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='更新章节分析结果中的人物和事件信息')
    parser.add_argument('--json-dir', required=True, help='章节JSON文件目录路径')
    parser.add_argument('--novel-dir', required=True, help='小说原文目录路径')
    parser.add_argument('--no-backup', action='store_true', help='不备份原文件')
    parser.add_argument('--start', type=int, default=1, help='起始章节号')
    parser.add_argument('--end', type=int, help='结束章节号（不指定则处理所有）')
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print("\n" + "="*60)
    print("🔄 更新章节人物和事件信息")
    print("="*60 + "\n")
    
    # 初始化LLM
    print("⚙️  初始化LLM...")
    llm = init_llm()
    print()
    
    # 初始化更新器
    updater = CharacterEventUpdater(llm)
    
    # 获取所有JSON文件（支持标题命名）
    json_files = []
    for filename in os.listdir(args.json_dir):
        if filename.endswith('.json') and not filename.endswith('.backup'):
            json_path = os.path.join(args.json_dir, filename)
            try:
                # 读取JSON文件获取章节号和标题
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                chapter_num = data.get('chapter_number')
                chapter_title = data.get('chapter_title', '')
                
                if chapter_num is not None:
                    if chapter_num >= args.start:
                        if args.end is None or chapter_num <= args.end:
                            # 使用章节标题作为显示名称（如果有）
                            display_name = chapter_title if chapter_title else filename
                            json_files.append((chapter_num, json_path, display_name))
            except Exception as e:
                print(f"  ⚠️  读取文件 {filename} 失败: {e}")
                continue
    
    if not json_files:
        print("❌ 未找到符合条件的JSON文件")
        return
    
    json_files.sort()
    total = len(json_files)
    
    print(f"📊 找到 {total} 个章节文件")
    print(f"📁 JSON目录: {args.json_dir}")
    print(f"📁 小说目录: {args.novel_dir}")
    print(f"💾 备份模式: {'关闭' if args.no_backup else '开启'}")
    print()
    
    # 处理每个文件
    success_count = 0
    fail_count = 0
    
    for idx, (chapter_num, json_file, display_name) in enumerate(json_files, 1):
        print(f"[{idx}/{total}] 处理章节 {chapter_num}: {display_name}")
        
        if updater.update_chapter_file(json_file, args.novel_dir, backup=not args.no_backup):
            success_count += 1
            print(f"  ✓ 完成\n")
        else:
            fail_count += 1
            print(f"  ✗ 失败\n")
        
        time.sleep(1)  # 避免请求过快
    
    # 打印统计信息
    print("\n" + "="*60)
    print("📊 处理完成")
    print("="*60)
    print(f"  总计: {total} 个文件")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {fail_count} 个")
    print()


if __name__ == '__main__':
    main()
