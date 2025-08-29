#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库名称检查脚本
用于检查导出文件中的数据库名称和结构信息
"""

import os
import sys
import gzip
import re
from typing import Dict, List, Optional

def check_export_file(file_path: str) -> Dict:
    """检查导出文件中的数据库信息"""
    result = {
        'file_path': file_path,
        'file_size': 0,
        'database_name': None,
        'tables': [],
        'has_structure': False,
        'has_data': False,
        'export_type': 'unknown'
    }
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return result
    
    # 获取文件大小
    result['file_size'] = os.path.getsize(file_path)
    
    try:
        # 尝试解压并读取文件
        if file_path.endswith('.gz'):
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                content = f.read()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # 查找数据库名称
        db_name_patterns = [
            r'CREATE DATABASE "([^"]+)"',
            r'CREATE DATABASE ([^\s;]+)',
            r'-- Database: ([^\s]+)',
            r'\\connect ([^\s]+)',
            r'USE ([^\s;]+)'
        ]
        
        for pattern in db_name_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result['database_name'] = match.group(1)
                break
        
        # 检查是否包含表结构
        if re.search(r'CREATE TABLE', content, re.IGNORECASE):
            result['has_structure'] = True
        
        # 检查是否包含数据
        if re.search(r'INSERT INTO', content, re.IGNORECASE):
            result['has_data'] = True
        
        # 确定导出类型
        if result['has_structure'] and result['has_data']:
            result['export_type'] = '完整数据库（结构和数据）'
        elif result['has_structure']:
            result['export_type'] = '仅结构'
        elif result['has_data']:
            result['export_type'] = '仅数据'
        else:
            result['export_type'] = '未知类型'
        
        # 提取表名
        table_pattern = r'CREATE TABLE (?:IF NOT EXISTS )?"?([^"\s(]+)"?'
        tables = re.findall(table_pattern, content, re.IGNORECASE)
        result['tables'] = list(set(tables))  # 去重
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return result
    
    return result

def print_export_file_info(result: Dict):
    """打印导出文件信息"""
    print(f"\n📋 导出文件信息:")
    print(f"   文件路径: {result['file_path']}")
    print(f"   文件大小: {result['file_size']:,} 字节 ({result['file_size']/1024:.1f} KB)")
    
    if result['database_name']:
        print(f"   🗄️  数据库名称: {result['database_name']}")
    else:
        print(f"   ⚠️  数据库名称: 未找到")
    
    print(f"   📊 导出类型: {result['export_type']}")
    print(f"   🏗️  包含结构: {'是' if result['has_structure'] else '否'}")
    print(f"   📊 包含数据: {'是' if result['has_data'] else '否'}")
    
    if result['tables']:
        print(f"   📋 表数量: {len(result['tables'])}")
        print(f"   📋 表列表:")
        for table in sorted(result['tables']):
            print(f"      - {table}")
    else:
        print(f"   ⚠️  表信息: 未找到")

def find_export_files(backup_dir: str = "backups") -> List[str]:
    """查找导出文件"""
    export_files = []
    
    if not os.path.exists(backup_dir):
        print(f"❌ 备份目录不存在: {backup_dir}")
        return export_files
    
    # 查找所有导出文件
    for file in os.listdir(backup_dir):
        if file.startswith("database_export_") and file.endswith(".sql.gz"):
            file_path = os.path.join(backup_dir, file)
            export_files.append(file_path)
    
    return sorted(export_files, reverse=True)  # 按时间倒序

def main():
    """主函数"""
    print("=== 数据库导出文件检查脚本 ===")
    
    # 查找导出文件
    export_files = find_export_files()
    
    if not export_files:
        print("❌ 未找到数据库导出文件")
        print("💡 请先运行: ./deploy.sh export-db")
        return
    
    print(f"📁 找到 {len(export_files)} 个导出文件:")
    
    # 检查每个文件
    for i, file_path in enumerate(export_files, 1):
        print(f"\n{i}. 检查文件: {os.path.basename(file_path)}")
        result = check_export_file(file_path)
        print_export_file_info(result)
    
    # 推荐最新的文件
    if export_files:
        latest_file = export_files[0]
        print(f"\n💡 推荐使用最新的导出文件:")
        print(f"   {latest_file}")
        
        # 检查最新文件
        result = check_export_file(latest_file)
        if result['database_name']:
            print(f"   🎯 数据库名称: {result['database_name']}")
            print(f"   📊 导出类型: {result['export_type']}")
            print(f"   📋 表数量: {len(result['tables'])}")
        else:
            print(f"   ⚠️  无法确定数据库名称，导入时请手动指定")
    
    print(f"\n🔧 使用方法:")
    print(f"   # 导入数据库")
    print(f"   ./deploy.sh import-db")
    print(f"   ")
    print(f"   # 手动导入到指定数据库")
    print(f"   gunzip -c {latest_file} | sudo -u postgres psql -d 目标数据库名")

if __name__ == "__main__":
    main()
