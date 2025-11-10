"""
修复不完整章节工具 - 扫描temp目录并合并已有结果
"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class ChapterRepairer:
    """章节修复器 - 从temp目录恢复不完整的章节"""
    
    REQUIRED_FIELDS = [
        'characters',
        'locations',
        'events',
        'world_elements',
        'writing_style_notes',
        'chapter_summary'
    ]
    
    def __init__(self, intermediate_dir: str):
        """
        初始化修复器
        
        Args:
            intermediate_dir: intermediate目录路径
        """
        self.intermediate_dir = Path(intermediate_dir)
        self.temp_dir = self.intermediate_dir / 'chapter_temp'
        self.summaries_dir = self.intermediate_dir / 'chapter_summaries'
        
        # 创建summaries目录（如果不存在）
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
    
    def scan_temp_chapters(self) -> List[Dict]:
        """
        扫描temp目录，找出所有有临时文件的章节
        
        Returns:
            章节信息列表
        """
        if not self.temp_dir.exists():
            print(f"❌ temp目录不存在: {self.temp_dir}")
            return []
        
        chapters_info = []
        
        for chapter_dir in sorted(self.temp_dir.glob("chapter_*")):
            if not chapter_dir.is_dir():
                continue
            
            # 提取章节号
            chapter_num = int(chapter_dir.name.replace("chapter_", ""))
            
            # 检查已有的字段
            available_fields = []
            for field in self.REQUIRED_FIELDS:
                field_file = chapter_dir / f"{field}.json"
                if field_file.exists():
                    available_fields.append(field)
            
            if available_fields:
                chapters_info.append({
                    'chapter_number': chapter_num,
                    'temp_dir': chapter_dir,
                    'available_fields': available_fields,
                    'missing_fields': [f for f in self.REQUIRED_FIELDS if f not in available_fields]
                })
        
        return chapters_info
    
    def check_summary_status(self, chapter_num: int) -> Dict:
        """
        检查章节摘要的状态
        
        Args:
            chapter_num: 章节号
            
        Returns:
            状态信息
        """
        summary_file = self.summaries_dir / f"chapter_{chapter_num:03d}.json"
        
        if not summary_file.exists():
            return {
                'exists': False,
                'complete': False,
                'has_fields': [],
                'missing_fields': self.REQUIRED_FIELDS
            }
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            has_fields = [f for f in self.REQUIRED_FIELDS if f in data]
            missing_fields = [f for f in self.REQUIRED_FIELDS if f not in data]
            
            return {
                'exists': True,
                'complete': len(missing_fields) == 0,
                'has_fields': has_fields,
                'missing_fields': missing_fields,
                'data': data
            }
        except Exception as e:
            return {
                'exists': True,
                'complete': False,
                'error': str(e),
                'has_fields': [],
                'missing_fields': self.REQUIRED_FIELDS
            }
    
    def merge_from_temp(self, chapter_num: int, temp_dir: Path, 
                        available_fields: List[str]) -> Optional[Dict]:
        """
        从temp目录合并字段到完整章节
        
        Args:
            chapter_num: 章节号
            temp_dir: temp目录路径
            available_fields: 可用字段列表
            
        Returns:
            合并后的完整数据
        """
        # 检查是否已有摘要文件
        summary_status = self.check_summary_status(chapter_num)
        
        if summary_status['complete']:
            return None  # 已完整，无需修复
        
        # 开始合并
        result = summary_status.get('data', {}) if summary_status['exists'] else {}
        
        # 从temp读取可用字段
        merged_count = 0
        for field in available_fields:
            if field in result:
                continue  # 已有该字段，跳过
            
            field_file = temp_dir / f"{field}.json"
            try:
                with open(field_file, 'r', encoding='utf-8') as f:
                    result[field] = json.load(f)
                merged_count += 1
            except Exception as e:
                print(f"      ⚠️  读取 {field}.json 失败: {e}")
        
        # 补充基本信息（如果缺失）
        if 'chapter_number' not in result:
            result['chapter_number'] = chapter_num
        
        # 保存修复后的文件
        if merged_count > 0 or not summary_status['exists']:
            output_file = self.summaries_dir / f"chapter_{chapter_num:03d}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        return None
    
    def repair_all(self, auto_confirm: bool = False, cleanup_temp: bool = False) -> Dict:
        """
        修复所有不完整的章节
        
        Args:
            auto_confirm: 自动确认，不询问
            cleanup_temp: 修复后清理temp目录
            
        Returns:
            修复统计信息
        """
        print("🔍 扫描temp目录...\n")
        
        temp_chapters = self.scan_temp_chapters()
        
        if not temp_chapters:
            print("✅ 没有找到temp文件，无需修复")
            return {'total': 0, 'repaired': 0, 'skipped': 0}
        
        print(f"📋 发现 {len(temp_chapters)} 个有临时文件的章节\n")
        
        # 分析需要修复的章节
        need_repair = []
        already_complete = []
        
        for chapter_info in temp_chapters:
            chapter_num = chapter_info['chapter_number']
            summary_status = self.check_summary_status(chapter_num)
            
            if summary_status['complete']:
                already_complete.append(chapter_num)
            else:
                # 计算可以补充的字段
                can_merge = [f for f in chapter_info['available_fields'] 
                           if f in summary_status['missing_fields']]
                
                if can_merge:
                    need_repair.append({
                        **chapter_info,
                        'can_merge': can_merge,
                        'summary_status': summary_status
                    })
        
        # 打印分析结果
        print("="*80)
        print(f"📊 分析结果:")
        print(f"  ✅ 已完整章节: {len(already_complete)}")
        print(f"  🔧 需要修复章节: {len(need_repair)}")
        print("="*80 + "\n")
        
        if already_complete:
            print(f"已完整章节: {', '.join(map(str, sorted(already_complete)))}\n")
        
        if not need_repair:
            print("✅ 所有章节都已完整！")
            return {'total': len(temp_chapters), 'repaired': 0, 'skipped': len(already_complete)}
        
        # 显示需要修复的详情
        print(f"🔧 需要修复的章节详情:\n")
        for item in need_repair:
            print(f"  📄 章节 {item['chapter_number']:03d}")
            print(f"     可补充字段 ({len(item['can_merge'])}): {', '.join(item['can_merge'])}")
            if item['summary_status']['exists']:
                print(f"     已有字段 ({len(item['summary_status']['has_fields'])}): {', '.join(item['summary_status']['has_fields'])}")
            else:
                print(f"     状态: 摘要文件不存在，将新建")
            print()
        
        # 询问确认
        if not auto_confirm:
            confirm = input(f"是否开始修复这 {len(need_repair)} 个章节？(y/n): ")
            if confirm.lower() != 'y':
                print("❌ 用户取消修复")
                return {'total': len(temp_chapters), 'repaired': 0, 'skipped': len(temp_chapters)}
        
        # 开始修复
        print("\n" + "="*80)
        print("🔧 开始修复...")
        print("="*80 + "\n")
        
        repaired_count = 0
        for item in need_repair:
            chapter_num = item['chapter_number']
            print(f"📝 修复章节 {chapter_num:03d}...")
            
            result = self.merge_from_temp(
                chapter_num,
                item['temp_dir'],
                item['available_fields']
            )
            
            if result:
                repaired_count += 1
                # 检查修复后的完整性
                final_status = self.check_summary_status(chapter_num)
                if final_status['complete']:
                    print(f"  ✅ 修复成功 - 已完整 (6/6)")
                else:
                    print(f"  ⚠️  部分修复 ({len(final_status['has_fields'])}/6)")
                    print(f"     仍缺失: {', '.join(final_status['missing_fields'])}")
            else:
                print(f"  ⚠️  无需修复或修复失败")
            print()
        
        # 清理temp目录
        if cleanup_temp and repaired_count > 0:
            print("\n🗑️  清理temp目录...")
            for item in need_repair:
                final_status = self.check_summary_status(item['chapter_number'])
                if final_status['complete']:
                    try:
                        shutil.rmtree(item['temp_dir'])
                        print(f"  ✓ 删除 {item['temp_dir'].name}")
                    except Exception as e:
                        print(f"  ⚠️  删除失败 {item['temp_dir'].name}: {e}")
        
        # 总结
        print("\n" + "="*80)
        print("✨ 修复完成！")
        print("="*80)
        print(f"📊 统计:")
        print(f"  总计章节: {len(temp_chapters)}")
        print(f"  已完整: {len(already_complete)}")
        print(f"  成功修复: {repaired_count}")
        print(f"  跳过: {len(temp_chapters) - repaired_count - len(already_complete)}")
        print("="*80 + "\n")
        
        return {
            'total': len(temp_chapters),
            'repaired': repaired_count,
            'skipped': len(already_complete),
            'still_incomplete': len(need_repair) - repaired_count
        }
    
    def generate_repair_report(self, output_file: str = "repair_report.json"):
        """
        生成修复报告
        
        Args:
            output_file: 输出文件名
        """
        temp_chapters = self.scan_temp_chapters()
        
        report = {
            'scan_time': str(Path.cwd()),
            'temp_chapters': [],
            'statistics': {
                'total_temp_chapters': len(temp_chapters),
                'complete_chapters': 0,
                'incomplete_chapters': 0,
                'missing_chapters': 0
            }
        }
        
        for chapter_info in temp_chapters:
            chapter_num = chapter_info['chapter_number']
            summary_status = self.check_summary_status(chapter_num)
            
            chapter_report = {
                'chapter_number': chapter_num,
                'temp_available_fields': chapter_info['available_fields'],
                'temp_missing_fields': chapter_info['missing_fields'],
                'summary_exists': summary_status['exists'],
                'summary_complete': summary_status['complete'],
                'summary_has_fields': summary_status['has_fields'],
                'summary_missing_fields': summary_status['missing_fields']
            }
            
            if summary_status['complete']:
                report['statistics']['complete_chapters'] += 1
            else:
                report['statistics']['incomplete_chapters'] += 1
            
            report['temp_chapters'].append(chapter_report)
        
        output_path = self.intermediate_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 修复报告已生成: {output_path}")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='修复不完整章节 - 从temp目录合并已提取的字段',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 扫描并修复（会询问确认）
  python repair_incomplete_chapters.py --intermediate /path/to/intermediate
  
  # 自动修复，不询问
  python repair_incomplete_chapters.py --intermediate /path/to/intermediate --auto-confirm
  
  # 修复后清理temp目录
  python repair_incomplete_chapters.py --intermediate /path/to/intermediate --auto-confirm --cleanup
  
  # 只生成报告，不修复
  python repair_incomplete_chapters.py --intermediate /path/to/intermediate --report-only
        """
    )
    
    parser.add_argument(
        '--intermediate',
        required=True,
        help='intermediate目录路径（包含chapter_temp和chapter_summaries）'
    )
    
    parser.add_argument(
        '--auto-confirm',
        action='store_true',
        help='自动确认修复，不询问'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='修复后清理已完整章节的temp目录'
    )
    
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='只生成报告，不执行修复'
    )
    
    args = parser.parse_args()
    
    # 创建修复器
    repairer = ChapterRepairer(args.intermediate)
    
    if args.report_only:
        repairer.generate_repair_report()
    else:
        repairer.repair_all(
            auto_confirm=args.auto_confirm,
            cleanup_temp=args.cleanup
        )


if __name__ == '__main__':
    main()
