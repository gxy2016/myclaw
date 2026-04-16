#!/usr/bin/env python3
"""
导出 ZIP 包脚本
将 Skill 打包成 ZIP 文件
"""

import os
import sys
import zipfile
from pathlib import Path


def export_zip(source_dir: str, output_zip: str, exclude_patterns: list = None):
    """
    导出 ZIP 包
    
    Args:
        source_dir: 源目录
        output_zip: 输出 ZIP 文件路径
        exclude_patterns: 排除的文件模式列表
    """
    if exclude_patterns is None:
        exclude_patterns = ['.git', '__pycache__', '*.pyc', '.DS_Store', '.versions']
    
    source_path = Path(source_dir)
    output_path = Path(output_zip)
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建 ZIP 文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            # 排除指定目录
            dirs[:] = [d for d in dirs if not any(
                pattern in d for pattern in ['.git', '__pycache__', '.versions']
            )]
            
            for file in files:
                # 排除指定文件
                if any(file.endswith(pat.lstrip('*')) for pat in exclude_patterns if pat.startswith('*')):
                    continue
                
                file_path = Path(root) / file
                
                # 计算相对路径
                arcname = file_path.relative_to(source_path.parent)
                
                # 添加到 ZIP
                zipf.write(file_path, arcname)
                print(f"添加：{arcname}")
    
    # 打印统计
    file_count = len(zipfile.ZipFile(output_path).namelist())
    file_size = output_path.stat().st_size
    
    print(f"\n导出完成:")
    print(f"  ZIP 文件：{output_path}")
    print(f"  文件数量：{file_count}")
    print(f"  文件大小：{file_size / 1024:.2f} KB")
    
    return output_path


def main():
    """主函数"""
    # 默认参数
    script_dir = Path(__file__).parent
    source_dir = script_dir
    version = "1.0.0"
    output_zip = script_dir.parent / f"prompt-version-control-v{version}.zip"
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        version = sys.argv[1]
        output_zip = script_dir.parent / f"prompt-version-control-v{version}.zip"
    
    print(f"开始导出 Prompt Version Control Skill v{version}...")
    print(f"源目录：{source_dir}")
    print(f"输出文件：{output_zip}")
    print()
    
    # 导出
    export_zip(str(source_dir), str(output_zip))
    
    print(f"\n✓ 导出成功！")
    print(f"  文件位置：{output_zip}")


if __name__ == "__main__":
    main()
