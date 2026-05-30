#!/bin/bash
# 启动脚本给 Render 使用

# 创建数据目录
mkdir -p server/data

# 初始化数据库
cd server
python -c "
from database.init_db import init_database
init_database()
print('Database initialized')
"

# 启动应用
exec python app_cloud.py