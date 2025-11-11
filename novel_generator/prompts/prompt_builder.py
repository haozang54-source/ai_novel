"""提示词构建器 - 动态加载系统上下文"""
import os
import platform
from datetime import datetime
from pathlib import Path


class PromptBuilder:
    """构建包含系统上下文的提示词"""
    
    def __init__(self, project_root: str = None):
        """
        初始化提示词构建器
        
        Args:
            project_root: 项目根目录,如果为None则自动检测
        """
        if project_root is None:
            # 自动检测项目根目录(向上查找到包含.git或Pipfile的目录)
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / '.git').exists() or (parent / 'Pipfile').exists():
                    project_root = str(parent)
                    break
            else:
                # 如果找不到,使用当前文件的上上上级目录
                project_root = str(Path(__file__).parent.parent.parent)
        
        self.project_root = project_root
        self.working_directory = os.getcwd()
        self.system_type = platform.system()
        
        # 加载系统上下文模板
        self.context_template = self._load_context_template()
    
    def _load_context_template(self) -> str:
        """加载系统上下文模板"""
        template_path = Path(__file__).parent / "system_context.md"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ 无法加载系统上下文模板: {e}")
            return "# 系统上下文\n\n项目根目录: {project_root}\n"
    
    def build_system_context(self) -> str:
        """构建包含动态信息的系统上下文"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        context = self.context_template.format(
            project_root=self.project_root,
            working_directory=self.working_directory,
            system_type=self.system_type,
            current_time=current_time
        )
        
        return context
    
    def build_research_prompt(self, query: str, context: str = "") -> str:
        """
        构建研究任务的完整提示词
        
        Args:
            query: 用户查询
            context: 额外的上下文信息
            
        Returns:
            完整的提示词
        """
        # 系统上下文
        system_context = self.build_system_context()
        
        # 构建完整提示词
        prompt = f"""{system_context}

---

## 你的任务

{query}
"""
        
        if context:
            prompt += f"\n## 额外背景信息\n\n{context}\n"
        
        prompt += """
---

## 执行要求

1. **严格遵守路径规则**: 所有工具调用必须使用绝对路径
2. **先探索后行动**: 不确定时先用 `list_directory` 查看
3. **精确引用**: 给出答案时引用具体的文件和行号
4. **深入分析**: 不要仅仅复述内容,要给出洞察和见解
5. **错误处理**: 如果文件不存在,尝试其他可能的路径

开始执行任务!
"""
        
        return prompt
    
    def build_analysis_prompt(self, topic: str, data_dir: str) -> str:
        """
        构建数据分析提示词
        
        Args:
            topic: 分析主题
            data_dir: 数据目录(相对路径)
            
        Returns:
            完整提示词
        """
        abs_data_dir = os.path.join(self.project_root, data_dir)
        
        query = f"""请分析关于"{topic}"的数据:

1. 列出 `{abs_data_dir}` 目录的内容
2. 识别关键数据文件
3. 读取并分析主要文件
4. 总结关键发现和洞察

数据目录: {abs_data_dir}
"""
        
        return self.build_research_prompt(query)
    
    def build_code_learning_prompt(self, code_dir: str, topic: str) -> str:
        """
        构建代码学习提示词
        
        Args:
            code_dir: 代码目录(相对路径)
            topic: 学习主题
            
        Returns:
            完整提示词
        """
        abs_code_dir = os.path.join(self.project_root, code_dir)
        
        query = f"""请学习关于"{topic}"的代码实现:

1. 列出 `{abs_code_dir}` 目录的代码文件
2. 读取关键代码文件
3. 分析实现方法和设计模式
4. 总结最佳实践和可改进之处

代码目录: {abs_code_dir}
"""
        
        return self.build_research_prompt(query)
