#!/usr/bin/env python3
"""在服务器上创建正确的projects.py文件"""

import subprocess

# 使用Python脚本在服务器上创建文件
python_script = '''
import os
content = """from fastapi import APIRouter
router = APIRouter(prefix="/projects")

@router.get("/")
async def get_projects():
    return {"message": "Projects API working"}
"""
with open("/home/dev/project/app/api/v1/projects.py", "w", encoding="utf-8") as f:
    f.write(content)
print("File created successfully")
'''

# 使用plink命令在服务器上运行Python脚本
cmd = f'plink -batch -ssh -pw 123 dev@192.168.1.215 "cd /home/dev/project/app/api/v1 && python3 -c \'{python_script}\'"'
print("正在使用Python脚本创建projects.py文件...")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(f"命令执行结果: {result.returncode}")
if result.stdout:
    print(f"输出: {result.stdout}")
if result.stderr:
    print(f"错误: {result.stderr}")
