"""支持工具调用的增强版智能体基类"""
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from .base_agent import BaseAgent
from ..tools.tool_manager import ToolManager


class BaseAgentWithTools(BaseAgent):
    """支持Function Calling的智能体基类"""
    
    def __init__(
        self, 
        llm=None, 
        agent_name: str = "BaseAgentWithTools",
        tools: Optional[List[Any]] = None,
        max_iterations: int = 10
    ):
        """
        初始化支持工具的智能体
        
        Args:
            llm: 语言模型实例
            agent_name: 智能体名称
            tools: 要绑定的工具列表,如果为None则使用所有文件系统工具
            max_iterations: 最大迭代次数,防止无限循环
        """
        super().__init__(llm, agent_name)
        
        # 初始化工具管理器
        self.tool_manager = ToolManager()
        
        # 设置工具
        if tools is None:
            # 默认使用文件系统工具
            self.tools = self.tool_manager.get_file_system_tools()
        else:
            self.tools = tools
        
        # 绑定工具到LLM
        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
            self.log(f"✅ 已绑定 {len(self.tools)} 个工具")
        else:
            self.llm_with_tools = self.llm
            self.log("⚠️ 未绑定任何工具")
        
        # 创建工具名称到工具对象的映射
        self.tools_map = {tool.name: tool for tool in self.tools}
        
        # 最大迭代次数
        self.max_iterations = max_iterations
        
        # 对话历史
        self.messages = []
    
    def invoke_with_tools(self, prompt: str, verbose: bool = True) -> str:
        """
        调用支持工具的LLM
        
        Args:
            prompt: 提示词
            verbose: 是否打印详细信息
            
        Returns:
            最终响应内容
        """
        # 初始化消息
        self.messages = [HumanMessage(content=prompt)]
        
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            
            if verbose:
                self.log(f"🔄 迭代 {iteration}/{self.max_iterations}")
            
            # 调用LLM
            try:
                response = self.llm_with_tools.invoke(self.messages)
            except Exception as e:
                error_msg = f"❌ LLM调用失败: {e}"
                self.log(error_msg)
                return error_msg
            
            # 添加AI响应到历史
            self.messages.append(response)
            
            # 检查是否有工具调用
            if not hasattr(response, 'tool_calls') or not response.tool_calls:
                # 没有工具调用,返回最终响应
                if verbose:
                    self.log("✅ 完成,无需调用工具")
                return response.content if hasattr(response, 'content') else str(response)
            
            # 执行工具调用
            if verbose:
                self.log(f"🔧 需要调用 {len(response.tool_calls)} 个工具")
            
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                if verbose:
                    self.log(f"  📌 调用工具: {tool_name}")
                    self.log(f"     参数: {tool_args}")
                
                # 执行工具
                try:
                    if tool_name in self.tools_map:
                        tool = self.tools_map[tool_name]
                        result = tool.invoke(tool_args)
                        
                        if verbose:
                            # 限制结果输出长度
                            result_preview = str(result)[:200]
                            if len(str(result)) > 200:
                                result_preview += "..."
                            self.log(f"     结果: {result_preview}")
                    else:
                        result = f"错误: 未找到工具 '{tool_name}'"
                        if verbose:
                            self.log(f"     ❌ {result}")
                except Exception as e:
                    result = f"工具执行错误: {str(e)}"
                    if verbose:
                        self.log(f"     ❌ {result}")
                
                # 添加工具结果到历史
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call['id']
                )
                self.messages.append(tool_message)
        
        # 达到最大迭代次数
        warning = f"⚠️ 达到最大迭代次数 {self.max_iterations},停止执行"
        self.log(warning)
        return warning
    
    def list_tools(self) -> Dict[str, str]:
        """列出当前智能体可用的工具"""
        return {tool.name: tool.description for tool in self.tools}
    
    def clear_history(self):
        """清空对话历史"""
        self.messages = []
        self.log("🗑️ 已清空对话历史")
