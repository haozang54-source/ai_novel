#!/usr/bin/env python3
"""
大模型服务连接测试脚本
用于验证Ollama或OpenAI模型服务是否正常可用
"""
import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from novel_generator.agents.base_agent import BaseAgent


def test_llm_connection():
    """测试LLM连接和基本功能"""
    print("=" * 60)
    print("🔍 大模型服务连接测试")
    print("=" * 60)
    
    # 显示当前配置信息
    print("\n📋 当前环境配置:")
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', '未设置')}")
    print(f"  OPENAI_MODEL: {os.getenv('OPENAI_MODEL', '未设置')}")
    print(f"  OPENAI_API_BASE: {os.getenv('OPENAI_API_BASE', '未设置')}")
    print(f"  OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', '未设置')}")
    print(f"  OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', '未设置')}")
    print(f"  LLM_TEMPERATURE: {os.getenv('LLM_TEMPERATURE', '未设置')}")
    
    # 检查必要的配置
    provider = os.getenv('LLM_PROVIDER', '').lower()
    if not provider:
        print("\n❌ 错误: LLM_PROVIDER 环境变量未设置")
        print("  请在.env文件中设置 LLM_PROVIDER=ollama 或 LLM_PROVIDER=openai")
        return False
    
    # 测试连接
    print(f"\n🚀 开始测试 {provider.upper()} 模型连接...")
    start_time = time.time()
    
    try:
        # 创建一个简单的测试智能体
        class TestAgent(BaseAgent):
            def run(self, input_data):
                return {"result": "Test completed"}
        
        # 初始化智能体（这将初始化LLM连接）
        test_agent = TestAgent(agent_name="TestAgent")
        print(f"✅ 成功初始化智能体和LLM连接")
        
        # 测试基本的LLM调用功能
        print("\n💬 测试LLM文本生成功能...")
        test_prompt = "请简单介绍一下你自己，用一句话回答。"
        response = test_agent.invoke_llm(test_prompt)
        
        if response and not response.startswith("❌"):
            print(f"✅ LLM调用成功!")
            print(f"📝 响应内容: {response[:100]}..." if len(response) > 100 else f"📝 响应内容: {response}")
        else:
            print(f"❌ LLM调用失败: {response}")
            return False
        
        end_time = time.time()
        print(f"\n⏱️  测试完成，耗时: {end_time - start_time:.2f} 秒")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        
        # 提供针对性的错误建议
        if "Ollama" in str(e) or provider == "ollama":
            print("\n💡 可能的解决方案:")
            print("  1. 确保Ollama服务已启动: ollama serve")
            print("  2. 确保已安装指定的模型: ollama pull", os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))
            print("  3. 检查OLLAMA_BASE_URL是否正确设置")
        
        elif provider == "openai":
            print("\n💡 可能的解决方案:")
            print("  1. 确保OPENAI_API_KEY已正确设置")
            print("  2. 检查OPENAI_API_BASE是否正确配置")
            print("  3. 确保网络连接正常且能访问API服务")
        
        return False


if __name__ == "__main__":
    success = test_llm_connection()
    print("\n" + "=" * 60)
    if success:
        print("🎉 大模型服务连接测试成功!")
    else:
        print("❌ 大模型服务连接测试失败，请检查配置和服务状态")
    print("=" * 60)
    sys.exit(0 if success else 1)