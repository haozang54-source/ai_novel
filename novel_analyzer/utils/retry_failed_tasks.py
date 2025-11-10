"""
重试失败任务工具 - 用于修复部分提取失败的章节
"""
import os
import json
from pathlib import Path
from typing import List, Dict


class FailedTaskRetry:
    """重试失败任务的工具类"""
    
    REQUIRED_FIELDS = [
        'characters',
        'locations',
        'events',
        'world_elements',
        'writing_style_notes',
        'chapter_summary'
    ]
    
    def __init__(self, chapter_summaries_dir: str):
        """
        初始化
        
        Args:
            chapter_summaries_dir: 章节摘要目录
        """
        self.summaries_dir = Path(chapter_summaries_dir)
    
    def find_incomplete_chapters(self) -> List[Dict]:
        """
        查找不完整的章节
        
        Returns:
            不完整章节列表，包含章节号和缺失字段
        """
        incomplete = []
        
        for json_file in sorted(self.summaries_dir.glob("chapter_*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                chapter_num = data.get('chapter_number')
                missing_fields = []
                
                for field in self.REQUIRED_FIELDS:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    incomplete.append({
                        'chapter_number': chapter_num,
                        'file': json_file.name,
                        'missing_fields': missing_fields,
                        'has_fields': [f for f in self.REQUIRED_FIELDS if f in data]
                    })
            
            except Exception as e:
                print(f"⚠️  读取 {json_file.name} 失败: {e}")
        
        return incomplete
    
    def print_report(self):
        """打印不完整章节报告"""
        incomplete = self.find_incomplete_chapters()
        
        if not incomplete:
            print("✅ 所有章节都完整！")
            return
        
        print(f"\n⚠️  发现 {len(incomplete)} 个不完整的章节：\n")
        print("=" * 80)
        
        for item in incomplete:
            print(f"📄 章节 {item['chapter_number']} ({item['file']})")
            print(f"   ❌ 缺失字段 ({len(item['missing_fields'])}): {', '.join(item['missing_fields'])}")
            print(f"   ✅ 已有字段 ({len(item['has_fields'])}): {', '.join(item['has_fields'])}")
            print()
        
        print("=" * 80)
        print(f"\n💡 修复建议：")
        print(f"   1. 删除不完整的章节JSON文件")
        print(f"   2. 重新运行 --use-v2 分析，会自动重新提取缺失章节")
        print(f"   3. 或者手动编辑JSON文件补全缺失字段\n")
    
    def export_missing_list(self, output_file: str = "missing_fields_report.json"):
        """
        导出缺失字段报告
        
        Args:
            output_file: 输出文件名
        """
        incomplete = self.find_incomplete_chapters()
        
        report = {
            'total_incomplete': len(incomplete),
            'incomplete_chapters': incomplete,
            'summary': {
                'total_chapters': len(list(self.summaries_dir.glob("chapter_*.json"))),
                'complete_chapters': len(list(self.summaries_dir.glob("chapter_*.json"))) - len(incomplete),
                'incomplete_ratio': f"{len(incomplete) / len(list(self.summaries_dir.glob('chapter_*.json'))) * 100:.2f}%"
            }
        }
        
        output_path = self.summaries_dir.parent / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 报告已导出到: {output_path}")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='检查章节分析完整性')
    parser.add_argument('--summaries-dir', required=True, help='章节摘要目录')
    parser.add_argument('--export', action='store_true', help='导出缺失字段报告')
    
    args = parser.parse_args()
    
    checker = FailedTaskRetry(args.summaries_dir)
    checker.print_report()
    
    if args.export:
        checker.export_missing_list()


if __name__ == '__main__':
    main()
