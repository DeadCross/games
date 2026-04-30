#!/bin/bash
cd /data/tank

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install pygame
else
    source venv/bin/activate
fi

# 运行游戏
python3 stickman_game.py
