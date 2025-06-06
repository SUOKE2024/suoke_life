"""
constants - 索克生活项目模块
"""

from enum import Enum
from typing import Final

"""
Corn Maze Service 常量定义

定义服务中使用的各种常量。
"""


# 迷宫相关常量
MAZE_MIN_SIZE: Final[int] = 5
MAZE_MAX_SIZE: Final[int] = 50
MAZE_DEFAULT_SIZE: Final[int] = 10

# 迷宫结束位置（相对于大小）
MAZE_END_X: Final[int] = -1  # 表示 size-1
MAZE_END_Y: Final[int] = -1  # 表示 size-1

# 分页常量
DEFAULT_PAGE_SIZE: Final[int] = 10
MAX_PAGE_SIZE: Final[int] = 100

# 缓存常量
CACHE_TTL_SECONDS: Final[int] = 3600  # 1小时
CACHE_KEY_PREFIX: Final[str] = "corn_maze"

# 移动方向常量
class Direction(Enum):
    """移动方向"""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

# 方向偏移量 (dx, dy)
DIRECTION_OFFSETS: Final[dict[Direction, tuple[int, int]]] = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0),
}

# 事件类型
class EventType(Enum):
    """事件类型"""
    NONE = "NONE"
    KNOWLEDGE = "KNOWLEDGE"
    CHALLENGE = "CHALLENGE"
    REWARD = "REWARD"
    OBSTACLE = "OBSTACLE"

# 健康主题相关常量
HEALTH_THEMES: Final[list[str]] = [
    "health",      # 健康养生
    "nutrition",   # 营养膳食
    "tcm",         # 中医养生
    "balance",     # 平衡调理
]

# 难度级别
DIFFICULTY_LEVELS: Final[list[str]] = [
    "easy",        # 简单
    "medium",      # 中等
    "hard",        # 困难
    "expert",      # 专家
]

# 节点类型权重（用于生成迷宫时的概率）
NODE_TYPE_WEIGHTS: Final[dict[str, float]] = {
    "PATH": 0.6,        # 路径 60%
    "WALL": 0.25,       # 墙壁 25%
    "KNOWLEDGE": 0.08,  # 知识点 8%
    "CHALLENGE": 0.05,  # 挑战 5%
    "REWARD": 0.02,     # 奖励 2%
}

# 评分系统
SCORING: Final[dict[str, int]] = {
    "MOVE": 1,           # 每次移动得分
    "KNOWLEDGE": 10,     # 知识点得分
    "CHALLENGE": 20,     # 挑战完成得分
    "REWARD": 50,        # 奖励得分
    "COMPLETION": 100,   # 完成迷宫得分
}

# 时间限制（秒）
TIME_LIMITS: Final[dict[str, int]] = {
    "easy": 1800,    # 30分钟
    "medium": 1200,  # 20分钟
    "hard": 900,     # 15分钟
    "expert": 600,   # 10分钟
}

# API版本
API_VERSION: Final[str] = "v1"
API_PREFIX: Final[str] = f"/api/{API_VERSION}"

# 服务信息
SERVICE_NAME: Final[str] = "corn-maze-service"
SERVICE_VERSION: Final[str] = "1.0.0"
SERVICE_DESCRIPTION: Final[str] = "Corn Maze Service for Health Education"

# HTTP 状态码
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_UNPROCESSABLE_ENTITY = 422

# 服务器端口
DEFAULT_GRPC_PORT = 50057
DEFAULT_HTTP_PORT = 51057

# 数据库配置
DEFAULT_POOL_SIZE = 10
DEFAULT_MAX_WORKERS = 10

# 分页配置
DEFAULT_PAGE = 1

# 方向常量
DIRECTION_NORTH = 0
DIRECTION_EAST = 1
DIRECTION_SOUTH = 2
DIRECTION_WEST = 3

# 性能阈值
SLOW_OPERATION_THRESHOLD = 5.0  # 秒
SLOW_REQUEST_THRESHOLD = 2.0    # 秒

# 难度级别
HIGH_DIFFICULTY_THRESHOLD = 4
KNOWLEDGE_NODES_BONUS_THRESHOLD = 5

# 缓存配置
MAX_PERFORMANCE_RECORDS = 1000

# 命令行参数
MIN_COMMAND_ARGS = 2

# 测试端口
TEST_GRPC_PORT = 60000

# 分页测试值
TEST_PAGE_NUMBER = 2
TEST_PAGE_SIZE = 5
