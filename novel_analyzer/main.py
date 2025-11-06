"""
爆款分析工作流主程序
"""
import os
import sys
import yaml
import argparse
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


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='爆款小说分析工具')
    parser.add_argument('--input', '-i', required=True, help='小说文件夹路径')
    parser.add_argument('--output', '-o', required=True, help='输出模板目录')
    parser.add_argument('--config', '-c', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print("\n" + "="*60)
    print("📚 爆款小说分析工具")
    print("="*60 + "\n")
    
    start_time = datetime.now()
    
    # 加载配置
    print("⚙️  加载配置...")
    config = load_config(args.config)
    
    # 初始化LLM
    print("🤖 初始化LLM...")
    llm = init_llm(config)
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    intermediate_dir = os.path.join(args.output, 'intermediate')
    os.makedirs(intermediate_dir, exist_ok=True)
    
    try:
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
        chapter_analyzer = ChapterAnalyzer(llm, config, intermediate_dir)
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
