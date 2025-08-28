#!/usr/bin/env python3
"""在服务器上创建简单的projects.py文件"""

import subprocess

# 简单的文件内容
content = '''from fastapi import APIRouter
router = APIRouter(prefix="/projects")

@router.get("/")
async def get_projects():
    return {"message": "Projects API working"}
'''

# 使用plink命令在服务器上创建文件
cmd = f'plink -batch -ssh -pw 123 dev@192.168.1.215 "cd /home/dev/project/app/api/v1 && cat > projects.py << EOF\n{content}\nEOF"'
print("正在创建简单的projects.py文件...")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(f"命令执行结果: {result.returncode}")
if result.stdout:
    print(f"输出: {result.stdout}")
if result.stderr:
    print(f"错误: {result.stderr}")
