"""
爆款分析工作流主程序
"""
import os
import sys
import yaml
import argparse
import time
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入LLM相关包
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzers.preprocessor import NovelPreprocessor
from analyzers.chapter_analyzer import ChapterAnalyzer
from analyzers.segment_summarizer import SegmentSummarizer
from analyzers.global_analyzer import GlobalAnalyzer
from analyzers.template_generator import TemplateGenerator


def load_config(config_path: str = None) -> dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def init_llm(config: dict):
    """
    初始化LLM（优先使用环境变量）
    
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
        print(f"✓ 使用 Ollama 模型")
        print(f"  模型: {model}")
        print(f"  地址: {base_url}")
    
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
        print(f"✓ 使用 OpenAI 兼容接口")
        print(f"  模型: {model}")
        print(f"  地址: {base_url}")
        print(f"  温度: {temperature}, 最大Token: {max_tokens}")
    
    else:
        raise ValueError(f"不支持的LLM provider: {provider}")
    
    return llm


def check_time_allowed(config: dict) -> bool:
    """
    检查当前时间是否在允许的运行时间段内
    
    Args:
        config: 配置字典
        
    Returns:
        是否允许运行
    """
    runtime_config = config.get('runtime', {})
    if not runtime_config:
        return True  # 如果没有配置运行时间限制，默认允许
    
    start_hour = runtime_config.get('start', 22)  # 默认晚上10点
    end_hour = runtime_config.get('end', 8)       # 默认早上8点
    
    current_hour = datetime.now().hour
    
    # 处理跨天的情况（如 22点到次日8点）
    if start_hour > end_hour:
        # 跨天：22点-24点 或 0点-8点
        allowed = current_hour >= start_hour or current_hour < end_hour
    else:
        # 不跨天：8点-22点
        allowed = start_hour <= current_hour < end_hour
    
    return allowed


def wait_for_allowed_time(config: dict):
    """
    等待到允许的运行时间段
    
    Args:
        config: 配置字典
    """
    runtime_config = config.get('runtime', {})
    if not runtime_config:
        return  # 如果没有配置运行时间限制，直接返回
    
    start_hour = runtime_config.get('start', 22)
    end_hour = runtime_config.get('end', 8)
    
    while not check_time_allowed(config):
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # 计算距离下次允许时间的小时数
        if start_hour > end_hour:  # 跨天
            if current_hour < start_hour and current_hour >= end_hour:
                hours_to_wait = start_hour - current_hour
            else:
                hours_to_wait = 1
        else:  # 不跨天
            hours_to_wait = start_hour - current_hour if current_hour < start_hour else 24 - current_hour + start_hour
        
        print(f"\n⏰ 当前时间 {current_time.strftime('%H:%M')} 不在允许的运行时间段内")
        print(f"   允许运行时间：{start_hour:02d}:00 - {end_hour:02d}:00")
        print(f"   预计等待约 {hours_to_wait} 小时")
        print(f"   将每5分钟检查一次...\n")
        
        time.sleep(300)  # 等待5分钟后重新检查


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='爆款小说分析工具')
    parser.add_argument('--input', '-i', required=True, help='小说文件夹路径')
    parser.add_argument('--output', '-o', required=True, help='输出模板目录')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--no-time-check', action='store_true', help='跳过运行时间检查')
    parser.add_argument('--use-v2', action='store_true', help='使用V2分段输出版本（更稳定，容错性更强）')
    parser.add_argument('--aggregate', action='store_true', help='聚合章节数据并生成分层存储')
    parser.add_argument('--model-type', default='gpt4', choices=['gpt4', 'claude', 'llama3'],
                       help='目标LLM类型（用于分块大小控制）')
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print("\n" + "="*60)
    print("📚 爆款小说分析工具")
    print("="*60 + "\n")
    
    start_time = datetime.now()
    
    # 加载配置
    print("⚙️  加载配置...")
    config = load_config(args.config)
    
    # 检查运行时间（除非使用了 --no-time-check 参数）
    if not args.no_time_check:
        print("🕐 检查运行时间...")
        wait_for_allowed_time(config)
        
        if check_time_allowed(config):
            runtime_config = config.get('runtime', {})
            if runtime_config:
                start = runtime_config.get('start', 22)
                end = runtime_config.get('end', 8)
                print(f"✓ 当前时间允许运行（允许时段：{start:02d}:00-{end:02d}:00）")
    else:
        print("⚠️  已跳过运行时间检查")
    
    # 初始化LLM
    print("🤖 初始化LLM...")
    llm = init_llm(config)
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    intermediate_dir = os.path.join(args.output, 'intermediate')
    os.makedirs(intermediate_dir, exist_ok=True)
    
    try:
        # 如果只是聚合数据，跳过分析流程
        if args.aggregate:
            from processors.layered_storage import LayeredStorageGenerator
            
            # 提取小说名称
            novel_name = os.path.basename(args.input.rstrip('/'))
            chapter_summaries_dir = os.path.join(args.output, 'intermediate', 'chapter_summaries')
            
            # 检查章节摘要目录是否存在
            if not os.path.exists(chapter_summaries_dir):
                print(f"❌ 章节摘要目录不存在: {chapter_summaries_dir}")
                print("   请先运行章节分析生成摘要数据")
                return
            
            # 创建分层存储生成器
            storage_dir = os.path.join(args.output, 'knowledge_base')
            generator = LayeredStorageGenerator(novel_name, storage_dir, args.model_type)
            
            # 生成所有层级
            generator.generate_all_layers(chapter_summaries_dir)
            return
        
        # 第一步：预处理
        print("\n" + "="*60)
        print("步骤 1: 文件预处理")
        print("="*60)
        preprocessor = NovelPreprocessor(args.input, config)
        chapters = preprocessor.load_and_process()
        
        if not chapters:
            print("❌ 没有可处理的章节，退出")
            return
        
        # 第二步：单章分析
        print("\n" + "="*60)
        print("步骤 2: 单章分析")
        print("="*60)
        
        # 再次检查时间（分析可能很长）
        if not args.no_time_check and not check_time_allowed(config):
            print("⚠️  已超出允许的运行时间段，暂停分析...")
            wait_for_allowed_time(config)
            print("✓ 恢复分析...")
        
        # 根据参数选择分析器版本
        if args.use_v2:
            from analyzers.chapter_analyzer_v2 import ChapterAnalyzerV2
            print("🔧 使用V2分段输出版本")
            chapter_analyzer = ChapterAnalyzerV2(llm, config, intermediate_dir, args.no_time_check)
        else:
            chapter_analyzer = ChapterAnalyzer(llm, config, intermediate_dir, args.no_time_check)
        
        chapter_results = chapter_analyzer.batch_analyze(chapters)
        
        if not chapter_results:
            print("❌ 单章分析失败，退出")
            return
        
        # 第三步：分段汇总
        print("\n" + "="*60)
        print("步骤 3: 分段汇总")
        print("="*60)
        segment_summarizer = SegmentSummarizer(llm, config, intermediate_dir)
        segment_results = segment_summarizer.summarize_segments(chapter_results)
        
        if not segment_results:
            print("❌ 分段汇总失败，退出")
            return
        
        # 第四步：整体分析
        print("\n" + "="*60)
        print("步骤 4: 整体分析")
        print("="*60)
        global_analyzer = GlobalAnalyzer(llm, config, intermediate_dir)
        global_analysis = global_analyzer.analyze_global(segment_results)
        
        if not global_analysis:
            print("❌ 整体分析失败，退出")
            return
        
        # 第五步：生成模板
        print("\n" + "="*60)
        print("步骤 5: 生成最终模板")
        print("="*60)
        template_generator = TemplateGenerator(config, args.output)
        success = template_generator.generate_all_templates(global_analysis)
        
        # 计算耗时
        end_time = datetime.now()
        duration = end_time - start_time
        
        # 完成
        print("\n" + "="*60)
        print("✅ 全部流程完成！")
        print("="*60)
        print(f"⏱️  总耗时: {duration}")
        print(f"📂 输出目录: {args.output}")
        print(f"\n📄 最终模板文件：")
        print(f"   1. world_bible.json        - 世界观圣经")
        print(f"   2. plot_framework.json     - 情节框架")
        print(f"   3. writing_guide.json      - 写作指南")
        print(f"   4. character_templates.json - 角色模板")
        print(f"   5. quality_criteria.json   - 质量标准")
        print(f"\n📂 中间结果：")
        print(f"   - 单章分析: {intermediate_dir}/chapter_summaries/")
        print(f"   - 分段汇总: {intermediate_dir}/segment_summaries/")
        print(f"   - 整体分析: {intermediate_dir}/global_analysis.json")
        
        if success:
            print(f"\n🎉 所有模板生成成功！")
        else:
            print(f"\n⚠️  部分模板生成失败，请检查输出目录")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
    except Exception as e:
        print(f"\n\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
