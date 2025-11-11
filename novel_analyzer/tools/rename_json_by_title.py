"""
批量重命名JSON文件：从数字命名改为标题命名

将 chapter_001.json, chapter_002.json 等
重命名为 第X章 标题.json 格式
"""
import os
import sys
import json
import argparse
from typing import Dict

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sanitize_filename(filename: str) -> str:
    """
    清理文件名中的不安全字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        安全的文件名
    """
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    safe_name = filename
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    return safe_name.strip() or 'untitled'


def rename_json_files(json_dir: str, dry_run: bool = False) -> Dict:
    """
    批量重命名JSON文件
    
    Args:
        json_dir: JSON文件目录
        dry_run: 是否仅预览，不实际重命名
        
    Returns:
        统计信息字典
    """
    if not os.path.isdir(json_dir):
        print(f"❌ 目录不存在: {json_dir}")
        return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    # 获取所有JSON文件
    json_files = []
    for filename in os.listdir(json_dir):
        if filename.endswith('.json') and not filename.endswith('.backup'):
            # 跳过已经是标题格式的文件
            if filename.startswith('第') or filename.startswith('chapter_'):
                json_files.append(filename)
    
    json_files.sort()
    
    if not json_files:
        print("❌ 未找到JSON文件")
        return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    print(f"📊 找到 {len(json_files)} 个JSON文件\n")
    
    stats = {
        "total": len(json_files),
        "success": 0,
        "failed": 0,
        "skipped": 0
    }
    
    for idx, filename in enumerate(json_files, 1):
        old_path = os.path.join(json_dir, filename)
        
        # 如果已经是标题格式，跳过
        if filename.startswith('第') and not filename.startswith('chapter_'):
            print(f"[{idx}/{len(json_files)}] ⏭️  跳过（已是标题格式）: {filename}")
            stats['skipped'] += 1
            continue
        
        try:
            # 读取JSON获取章节标题
            with open(old_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chapter_title = data.get('chapter_title', '')
            chapter_number = data.get('chapter_number')
            
            if not chapter_title:
                # 如果没有标题，使用章节号
                if chapter_number is not None:
                    chapter_title = f"第{chapter_number}章"
                else:
                    print(f"[{idx}/{len(json_files)}] ⚠️  缺少标题和章节号: {filename}")
                    stats['failed'] += 1
                    continue
            
            # 生成新文件名
            safe_title = sanitize_filename(chapter_title)
            new_filename = f"{safe_title}.json"
            new_path = os.path.join(json_dir, new_filename)
            
            # 检查新文件是否已存在
            if os.path.exists(new_path) and new_path != old_path:
                print(f"[{idx}/{len(json_files)}] ⚠️  目标文件已存在: {new_filename}")
                stats['failed'] += 1
                continue
            
            # 显示重命名操作
            if dry_run:
                print(f"[{idx}/{len(json_files)}] 📝 预览:")
                print(f"    {filename}")
                print(f"  → {new_filename}")
                stats['success'] += 1
            else:
                # 执行重命名
                os.rename(old_path, new_path)
                print(f"[{idx}/{len(json_files)}] ✓ 重命名成功:")
                print(f"    {filename}")
                print(f"  → {new_filename}")
                stats['success'] += 1
        
        except json.JSONDecodeError as e:
            print(f"[{idx}/{len(json_files)}] ❌ JSON解析失败: {filename}")
            print(f"    错误: {e}")
            stats['failed'] += 1
        
        except Exception as e:
            print(f"[{idx}/{len(json_files)}] ❌ 重命名失败: {filename}")
            print(f"    错误: {e}")
            stats['failed'] += 1
        
        print()
    
    return stats


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量重命名JSON文件为标题格式')
    parser.add_argument('--json-dir', required=True, help='JSON文件目录路径')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际重命名')
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print("\n" + "="*60)
    print("📝 批量重命名JSON文件")
    print("="*60 + "\n")
    
    if args.dry_run:
        print("⚠️  预览模式：仅显示重命名操作，不实际执行\n")
    
    print(f"📁 目标目录: {args.json_dir}\n")
    
    # 执行重命名
    stats = rename_json_files(args.json_dir, dry_run=args.dry_run)
    
    # 打印统计信息
    print("="*60)
    print("📊 重命名统计")
    print("="*60)
    print(f"  总计: {stats['total']} 个文件")
    print(f"  成功: {stats['success']} 个")
    print(f"  失败: {stats['failed']} 个")
    print(f"  跳过: {stats['skipped']} 个")
    print()
    
    if args.dry_run and stats['success'] > 0:
        print("💡 预览完成，使用 --dry-run=false 执行实际重命名")
        print()


if __name__ == '__main__':
    main()
