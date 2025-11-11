"""工具管理器 - 集中管理所有可用的工具"""
import sys
import importlib.util
from pathlib import Path
from typing import List, Dict, Any


# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 直接导入已经用 @tool 装饰的工具函数
tools_path = project_root / "tools" / "implementations" / "file_system"

def _load_tool(module_name: str, function_name: str):
    """动态加载工具(已使用@tool装饰)"""
    module_path = tools_path / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


class ToolManager:
    """管理和提供可用工具"""
    
    def __init__(self):
        """初始化工具管理器"""
        self._tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Any]:
        """注册所有可用工具"""
        tools = {}
        
        # 文件系统工具 - 这些函数已经用 @tool 装饰
        tools['read_file'] = _load_tool("read_file", "read_file")
        tools['write_file'] = _load_tool("write_file", "write_file")
        tools['list_directory'] = _load_tool("list_directory", "list_directory")
        tools['search_file_content'] = _load_tool("search_file_content", "search_file_content")
        tools['get_current_time'] = _load_tool("get_current_time", "get_current_time")
        
        return tools
    
    def get_all_tools(self) -> List[Any]:
        """获取所有可用工具"""
        return list(self._tools.values())
    
    def get_tools_by_names(self, tool_names: List[str]) -> List[Any]:
        """根据名称获取指定工具"""
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_file_system_tools(self) -> List[Any]:
        """获取文件系统相关工具"""
        fs_tools = ['read_file', 'write_file', 'list_directory', 'search_file_content']
        return self.get_tools_by_names(fs_tools)
    
    def list_available_tools(self) -> Dict[str, str]:
        """列出所有可用工具及其描述"""
        return {
            name: getattr(tool, 'description', str(tool))
            for name, tool in self._tools.items()
        }
