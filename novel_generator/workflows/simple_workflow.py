"""简单的端到端工作流"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List
from ..agents import DirectorAgent, OutlinerAgent, SceneWriterAgent, CriticAgent


class SimpleWorkflow:
    """端到端Demo工作流: Director → Outliner → SceneWriter → Critic"""
    
    def __init__(self, llm=None, output_dir="./generated_novels"):
        """
        初始化工作流
        
        Args:
            llm: 共享的LLM实例
            output_dir: 输出目录
        """
        self.llm = llm
        self.output_dir = output_dir
        
        # 初始化智能体
        self.director = DirectorAgent(llm)
        self.outliner = OutlinerAgent(llm)
        self.scene_writer = SceneWriterAgent(llm)
        self.critic = CriticAgent(llm)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        print("=" * 60)
        print("🎬 AI小说生成系统 - 端到端Demo")
        print("   工作流: Director → Outliner → SceneWriter → Critic")
        print("=" * 60)
    
    def create_novel(self, user_theme: str, target_length: int = 10000, 
                    genre: str = "玄幻", auto_mode: bool = False) -> Dict[str, Any]:
        """
        创作完整小说
        
        Args:
            user_theme: 用户输入的主题/想法
            target_length: 目标总字数
            genre: 小说类型
            auto_mode: 是否自动模式(跳过人工审阅)
            
        Returns:
            生成的小说数据
        """
        print(f"\n📖 开始创作小说")
        print(f"   主题: {user_theme}")
        print(f"   类型: {genre}")
        print(f"   目标字数: {target_length}字")
        print(f"   模式: {'自动' if auto_mode else '人工审阅'}")
        print()
        
        # 阶段1: Director规划
        print("\n" + "=" * 60)
        print("阶段1: 📋 总导演规划")
        print("=" * 60)
        
        plan_result = self.director.run({
            "user_theme": user_theme,
            "target_length": target_length,
            "genre": genre
        })
        
        # 阶段2: Outliner生成大纲
        print("\n" + "=" * 60)
        print("阶段2: 📝 大纲师生成大纲")
        print("=" * 60)
        
        outline_result = self.outliner.run({
            "story_concept": plan_result["story_concept"],
            "target_chapters": plan_result["target_chapters"],
            "chapter_length": plan_result["chapter_length"],
            "genre": genre
        })
        
        # 人工审阅大纲
        if not auto_mode:
            print("\n" + "=" * 60)
            print("👤 人工审阅点 - 大纲确认")
            print("=" * 60)
            self._display_outline(outline_result["outline"])
            
            if not self._confirm_outline():
                print("❌ 大纲被拒绝,工作流结束")
                return {"status": "rejected", "stage": "outline"}
        
        # 阶段3: SceneWriter逐章创作
        print("\n" + "=" * 60)
        print("阶段3: ✍️ 场景作家创作章节")
        print("=" * 60)
        
        chapters_content = []
        previous_content = ""
        
        for chapter_info in outline_result["outline"]:
            print(f"\n--- 第{chapter_info['chapter_num']}章 ---")
            
            # 生成章节内容
            chapter_result = self.scene_writer.run({
                "chapter_info": chapter_info,
                "story_context": plan_result["story_concept"],
                "target_length": plan_result["chapter_length"],
                "genre": genre,
                "previous_content": previous_content
            })
            
            # 阶段4: Critic评审
            print(f"\n🔍 评审第{chapter_info['chapter_num']}章...")
            
            evaluation = self.critic.run({
                "content": chapter_result["content"],
                "chapter_info": chapter_info,
                "story_context": plan_result["story_concept"]
            })
            
            # 人工审阅章节
            if not auto_mode:
                print("\n" + "-" * 60)
                print(f"👤 人工审阅 - 第{chapter_info['chapter_num']}章")
                print("-" * 60)
                
                action = self._review_chapter(chapter_result, evaluation)
                
                if action == "skip_review":
                    auto_mode = True  # 切换到自动模式
                elif action == "reject":
                    print(f"❌ 第{chapter_info['chapter_num']}章被拒绝,工作流结束")
                    return {"status": "rejected", "stage": f"chapter_{chapter_info['chapter_num']}"}
                elif action == "regenerate":
                    # TODO: 实现重新生成逻辑
                    print("⚠️ 重新生成功能待实现,本次接受当前内容")
            
            # 保存章节
            chapters_content.append({
                "chapter_num": chapter_info['chapter_num'],
                "title": chapter_info['title'],
                "content": chapter_result["content"],
                "word_count": chapter_result["word_count"],
                "evaluation": evaluation
            })
            
            # 更新前文上下文
            previous_content = chapter_result["content"]
        
        # 保存完整小说
        novel_data = {
            "metadata": {
                "theme": user_theme,
                "genre": genre,
                "created_at": datetime.now().isoformat(),
                "total_chapters": len(chapters_content),
                "total_words": sum(ch["word_count"] for ch in chapters_content)
            },
            "plan": plan_result,
            "outline": outline_result["outline"],
            "chapters": chapters_content
        }
        
        # 保存到文件
        output_path = self._save_novel(novel_data)
        
        # 显示完成信息
        print("\n" + "=" * 60)
        print("🎉 小说创作完成!")
        print("=" * 60)
        print(f"📊 统计信息:")
        print(f"   总章节数: {novel_data['metadata']['total_chapters']}")
        print(f"   总字数: {novel_data['metadata']['total_words']}")
        print(f"   平均每章: {novel_data['metadata']['total_words'] // novel_data['metadata']['total_chapters']}字")
        print(f"\n💾 已保存到: {output_path}")
        print("=" * 60)
        
        return novel_data
    
    def _display_outline(self, outline: List[Dict]):
        """显示大纲供审阅"""
        print("\n📋 故事大纲:")
        print("-" * 60)
        for chapter in outline:
            print(f"\n第{chapter['chapter_num']}章: {chapter['title']}")
            print(f"摘要: {chapter['summary']}")
            if chapter['key_events']:
                print(f"关键事件: {', '.join(chapter['key_events'])}")
            print(f"冲突: {chapter['conflicts']}")
            print(f"情感: {chapter['emotional_beat']}")
        print("-" * 60)
    
    def _confirm_outline(self) -> bool:
        """人工确认大纲"""
        while True:
            response = input("\n是否接受此大纲? (y=接受 / n=拒绝): ").strip().lower()
            if response in ['y', 'yes', '是', '接受']:
                return True
            elif response in ['n', 'no', '否', '拒绝']:
                return False
            else:
                print("⚠️ 请输入 y 或 n")
    
    def _review_chapter(self, chapter_result: Dict, evaluation: Dict) -> str:
        """
        人工审阅章节
        
        Returns:
            'accept' | 'reject' | 'regenerate' | 'skip_review'
        """
        # 显示章节内容(前500字)
        content = chapter_result["content"]
        preview = content[:500] + "..." if len(content) > 500 else content
        
        print(f"\n📄 章节预览:")
        print("-" * 60)
        print(preview)
        print("-" * 60)
        
        # 显示评审结果
        print(f"\n🤖 AI评分: {evaluation['overall_score']}/10")
        print(f"   可读性: {evaluation['readability']}/10")
        print(f"   情节: {evaluation['plot_consistency']}/10")
        print(f"   文笔: {evaluation['writing_quality']}/10")
        
        if evaluation['highlights']:
            print(f"\n✨ 亮点: {', '.join(evaluation['highlights'][:2])}")
        if evaluation['issues']:
            print(f"⚠️ 问题: {', '.join(evaluation['issues'][:2])}")
        
        # 用户选择
        print("\n请选择操作:")
        print("  1. 接受并继续")
        print("  2. 拒绝(停止创作)")
        print("  3. 重新生成本章")
        print("  4. 跳过后续审阅(自动模式)")
        
        while True:
            choice = input("\n请输入选择 (1-4): ").strip()
            if choice == '1':
                return 'accept'
            elif choice == '2':
                return 'reject'
            elif choice == '3':
                return 'regenerate'
            elif choice == '4':
                return 'skip_review'
            else:
                print("⚠️ 请输入 1-4")
    
    def _save_novel(self, novel_data: Dict) -> str:
        """保存小说到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        theme_short = novel_data['metadata']['theme'][:10].replace(' ', '_')
        
        # 创建项目目录
        project_dir = os.path.join(self.output_dir, f"{theme_short}_{timestamp}")
        os.makedirs(project_dir, exist_ok=True)
        
        # 保存JSON格式(完整数据)
        json_path = os.path.join(project_dir, "novel_data.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(novel_data, f, ensure_ascii=False, indent=2)
        
        # 保存TXT格式(阅读友好)
        txt_path = os.path.join(project_dir, "novel.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"标题: {novel_data['metadata']['theme']}\n")
            f.write(f"类型: {novel_data['metadata']['genre']}\n")
            f.write(f"创作时间: {novel_data['metadata']['created_at']}\n")
            f.write(f"总字数: {novel_data['metadata']['total_words']}\n")
            f.write("\n" + "=" * 60 + "\n\n")
            
            for chapter in novel_data['chapters']:
                f.write(f"第{chapter['chapter_num']}章 {chapter['title']}\n\n")
                f.write(chapter['content'])
                f.write("\n\n" + "-" * 60 + "\n\n")
        
        return txt_path
