"""研究型智能体 - 能够读取和分析本地文件"""
from typing import Dict, Any, Optional
from .base_agent_with_tools import BaseAgentWithTools
from ..prompts.prompt_builder import PromptBuilder


class ResearchAgent(BaseAgentWithTools):
    """
    研究型智能体
    
    能力:
    - 读取本地文件
    - 搜索文件内容
    - 分析文件结构
    - 基于文件内容生成洞察
    """
    
    def __init__(self, llm=None, project_root: Optional[str] = None):
        """
        初始化研究型智能体
        
        Args:
            llm: 语言模型实例
            project_root: 项目根目录,如果为None则自动检测
        """
        super().__init__(
            llm=llm,
            agent_name="ResearchAgent",
            tools=None,  # 使用默认文件系统工具
            max_iterations=15  # 研究任务可能需要更多迭代
        )
        
        # 初始化提示词构建器
        self.prompt_builder = PromptBuilder(project_root=project_root)
        self.log(f"📁 项目根目录: {self.prompt_builder.project_root}")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行研究任务
        
        Args:
            input_data: 输入数据,应包含:
                - query: 研究问题或任务
                - context: 可选的上下文信息
                
        Returns:
            研究结果
        """
        query = input_data.get('query', '')
        context = input_data.get('context', '')
        verbose = input_data.get('verbose', True)
        
        if not query:
            return {
                'status': 'error',
                'message': '❌ 缺少研究问题(query)'
            }
        
        # 使用提示词构建器构建提示词
        prompt = self.prompt_builder.build_research_prompt(query, context)
        
        # 执行研究
        self.log("🔍 开始研究任务...")
        result = self.invoke_with_tools(prompt, verbose=verbose)
        
        return {
            'status': 'success',
            'query': query,
            'result': result,
            'tool_calls_count': len([m for m in self.messages if hasattr(m, 'tool_calls') and m.tool_calls]),
            'messages': self.messages
        }
    

    
    def analyze_novel_data(self, novel_name: str, data_dir: str = "demo_output") -> Dict[str, Any]:
        """
        分析小说数据
        
        Args:
            novel_name: 小说名称
            data_dir: 数据目录(相对路径)
            
        Returns:
            分析结果
        """
        prompt = self.prompt_builder.build_analysis_prompt(
            topic=f"《{novel_name}》",
            data_dir=data_dir
        )
        
        return self.run({'query': prompt, 'verbose': True})
    
    def learn_from_code(self, code_dir: str, topic: str) -> Dict[str, Any]:
        """
        从代码中学习
        
        Args:
            code_dir: 代码目录(相对路径)
            topic: 要学习的主题
            
        Returns:
            学习结果
        """
        prompt = self.prompt_builder.build_code_learning_prompt(
            code_dir=code_dir,
            topic=topic
        )
        
        return self.run({'query': prompt, 'verbose': True})
