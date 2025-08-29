#!/usr/bin/env python3
"""
批量修复Python文件编码问题
"""
import os
import glob

def fix_file_encoding(file_path):
    """修复单个文件的编码问题"""
    try:
        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 检测编码
        if content.startswith(b'\xff\xfe'):  # UTF-16 LE
            # 转换为UTF-8
            content = content.decode('utf-16-le')
            # 移除CRLF
            content = content.replace('\r\n', '\n')
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"修复UTF-16编码: {file_path}")
        elif b'\r\n' in content:  # 有CRLF
            # 移除CRLF
            content = content.decode('utf-8')
            content = content.replace('\r\n', '\n')
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"修复CRLF: {file_path}")
        else:
            print(f"无需修复: {file_path}")
            
    except Exception as e:
        print(f"修复失败 {file_path}: {e}")

def main():
    """主函数"""
    # 查找所有Python文件
    python_files = glob.glob('app/**/*.py', recursive=True)
    
    print(f"找到 {len(python_files)} 个Python文件")
    
    # 修复每个文件
    for file_path in python_files:
        fix_file_encoding(file_path)
    
    print("编码修复完成！")

if __name__ == "__main__":
    main()
