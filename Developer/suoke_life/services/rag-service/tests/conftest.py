import sys
import os
from pathlib import Path

# 将src目录添加到Python路径
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir)) 