"""基础智能体类"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

# 加载环境变量
load_dotenv()


class BaseAgent(ABC):
    """所有智能体的基类"""
    
    def __init__(self, llm=None, agent_name: str = "BaseAgent"):
        """
        初始化智能体
        
        Args:
            llm: 语言模型实例,如果为None则使用默认配置
            agent_name: 智能体名称
        """
        self.agent_name = agent_name
        self.llm = llm or self._create_default_llm()
        self.memory = {}
        
    def _create_default_llm(self):
        """创建默认的LLM实例,从.env读取配置"""
        # 从环境变量读取配置
        llm_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        if llm_provider == "ollama":
            try:
                self.log(f"🤖 使用 Ollama 模型: {ollama_model}")
                return ChatOllama(
                    model=ollama_model,
                    temperature=temperature
                )
            except Exception as e:
                print(f"⚠️ Ollama初始化失败: {e}")
                print(f"💡 请确保 Ollama 已启动: ollama serve")
                print(f"💡 并安装模型: ollama pull {ollama_model}")
                raise
        elif llm_provider == "openai":
            try:
                self.log(f"🤖 使用 OpenAI 模型: {openai_model}")
                return ChatOpenAI(
                    model=openai_model,
                    temperature=temperature
                )
            except Exception as e:
                print(f"⚠️ OpenAI初始化失败: {e}")
                print(f"💡 请检查 OPENAI_API_KEY 是否配置正确")
                raise
        else:
            raise Exception(f"❌ 不支持的 LLM_PROVIDER: {llm_provider}，请使用 'ollama' 或 'openai'")
    
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行智能体的主要任务
        
        Args:
            input_data: 输入数据
            
        Returns:
            执行结果
        """
        pass
    
    def invoke_llm(self, prompt: str) -> str:
        """
        调用LLM生成内容
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的内容
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"❌ LLM调用失败: {e}"
    
    def log(self, message: str):
        """记录日志"""
        print(f"[{self.agent_name}] {message}")
