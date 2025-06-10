"""
maze - 索克生活项目模块
"""

from datetime import UTC, datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Any
from uuid import UUID, uuid4

"""
迷宫数据模型

定义迷宫相关的数据结构和业务模型。
"""




class MazeTheme(str, Enum):
    """迷宫主题枚举"""
    HEALTH = "health"
    NUTRITION = "nutrition"
    TCM = "tcm"
    BALANCE = "balance"

class MazeDifficulty(str, Enum):
    """迷宫难度枚举"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"

class NodeType(str, Enum):
    """节点类型枚举"""
    START = "start"
    END = "end"
    PATH = "path"
    WALL = "wall"
    KNOWLEDGE = "knowledge"
    CHALLENGE = "challenge"
    TREASURE = "treasure"

class MazeNode(BaseModel):
    """迷宫节点"""
    model_config = {"use_enum_values": True}

    x: int = Field(description = "X坐标")
    y: int = Field(description = "Y坐标")
    node_type: NodeType = Field(description = "节点类型")
    content: dict[str, Any] | None = Field(default = None, description = "节点内容")
    is_visited: bool = Field(default = False, description = "是否已访问")
    connections: list[tuple[int, int]] = Field(default_factory = list, description = "连接的节点坐标")

class Maze(BaseModel):
    """迷宫模型"""
    model_config = {"use_enum_values": True}

    id: UUID = Field(default_factory = uuid4, description = "迷宫ID")
    name: str = Field(description = "迷宫名称", min_length = 1, max_length = 100)
    description: str | None = Field(default = None, description = "迷宫描述", max_length = 500)
    size: int = Field(description = "迷宫大小", ge = 5, le = 100)
    theme: MazeTheme = Field(description = "迷宫主题")
    difficulty: MazeDifficulty = Field(description = "难度级别")
    is_public: bool = Field(default = False, description = "是否公开")
    creator_id: UUID = Field(description = "创建者ID")

    # 迷宫结构
    nodes: list[list[MazeNode]] = Field(description = "迷宫节点矩阵")
    start_position: tuple[int, int] = Field(description = "起始位置")
    end_position: tuple[int, int] = Field(description = "结束位置")

    # 元数据
    created_at: datetime = Field(default_factory = lambda: datetime.now(UTC), description = "创建时间")
    updated_at: datetime = Field(default_factory = lambda: datetime.now(UTC), description = "更新时间")

    # 统计信息
    total_nodes: int = Field(default = 0, description = "总节点数")
    knowledge_nodes: int = Field(default = 0, description = "知识节点数")
    challenge_nodes: int = Field(default = 0, description = "挑战节点数")
    completion_count: int = Field(default = 0, description = "完成次数")
    average_completion_time: float | None = Field(default = None, description = "平均完成时间(秒)")

    @field_validator("nodes")
    @classmethod
    def validate_nodes_size(cls, v: list[list[MazeNode]], info: Any) -> list[list[MazeNode]]:
        """验证节点矩阵大小"""
        # 在 Pydantic v2 中，我们需要从 info.data 获取其他字段的值
        size = info.data.get("size", 0) if info.data else 0
        if len(v) ! = size or any(len(row) ! = size for row in v):
            raise ValueError(f"Nodes matrix must be {size}x{size}")
        return v

    @field_validator("start_position", "end_position")
    @classmethod
    def validate_position(cls, v: tuple[int, int], info: Any) -> tuple[int, int]:
        """验证位置坐标"""
        size = info.data.get("size", 0) if info.data else 0
        x, y = v
        if not (0 < = x < size and 0 < = y < size):
            raise ValueError(f"Position must be within maze bounds (0, 0) to ({size - 1}, {size - 1})")
        return v

    def get_node(self, x: int, y: int) -> MazeNode | None:
        """获取指定位置的节点"""
        if 0 < = x < self.size and 0 < = y < self.size:
            return self.nodes[y][x]
        return None

    def set_node(self, x: int, y: int, node: MazeNode) -> None:
        """设置指定位置的节点"""
        if 0 < = x < self.size and 0 < = y < self.size:
            self.nodes[y][x] = node
            self.updated_at = datetime.now(UTC)

    def get_neighbors(self, x: int, y: int) -> list[MazeNode]:
        """获取相邻节点"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, - 1), ( - 1, 0)]:
            nx, ny = x + dx, y + dy
            node = self.get_node(nx, ny)
            if node:
                neighbors.append(node)
        return neighbors

class UserMaze(BaseModel):
    """用户迷宫关联"""
    id: UUID = Field(default_factory = uuid4, description = "关联ID")
    user_id: UUID = Field(description = "用户ID")
    maze_id: UUID = Field(description = "迷宫ID")

    # 权限
    can_edit: bool = Field(default = False, description = "是否可编辑")
    can_share: bool = Field(default = False, description = "是否可分享")

    # 时间戳
    created_at: datetime = Field(default_factory = lambda: datetime.now(UTC), description = "创建时间")
    last_accessed_at: datetime | None = Field(default = None, description = "最后访问时间")

class ProgressStatus(str, Enum):
    """进度状态枚举"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class MazeProgress(BaseModel):
    """迷宫进度"""
    id: UUID = Field(default_factory = uuid4, description = "进度ID")
    user_id: UUID = Field(description = "用户ID")
    maze_id: UUID = Field(description = "迷宫ID")

    # 进度信息
    status: ProgressStatus = Field(default = ProgressStatus.NOT_STARTED, description = "进度状态")
    current_position: tuple[int, int] = Field(description = "当前位置")
    visited_nodes: list[tuple[int, int]] = Field(default_factory = list, description = "已访问节点")
    collected_items: list[str] = Field(default_factory = list, description = "收集的物品")

    # 统计信息
    start_time: datetime | None = Field(default = None, description = "开始时间")
    end_time: datetime | None = Field(default = None, description = "结束时间")
    total_time: float | None = Field(default = None, description = "总用时(秒)")
    steps_count: int = Field(default = 0, description = "步数")
    hints_used: int = Field(default = 0, description = "使用提示次数")

    # 得分和奖励
    score: int = Field(default = 0, description = "得分")
    knowledge_gained: list[str] = Field(default_factory = list, description = "获得的知识")
    achievements: list[str] = Field(default_factory = list, description = "获得的成就")

    # 时间戳
    created_at: datetime = Field(default_factory = lambda: datetime.now(UTC), description = "创建时间")
    updated_at: datetime = Field(default_factory = lambda: datetime.now(UTC), description = "更新时间")

    model_config = {"use_enum_values": True}

    def add_visited_node(self, x: int, y: int) -> None:
        """添加已访问节点"""
        position = (x, y)
        if position not in self.visited_nodes:
            self.visited_nodes.append(position)
            self.steps_count + = 1
            self.updated_at = datetime.now(UTC)

    def complete_maze(self) -> None:
        """完成迷宫"""
        self.status = ProgressStatus.COMPLETED
        self.end_time = datetime.now(UTC)
        if self.start_time:
            self.total_time = (self.end_time - self.start_time).total_seconds()
        self.updated_at = datetime.now(UTC)

    def abandon_maze(self) -> None:
        """放弃迷宫"""
        self.status = ProgressStatus.ABANDONED
        self.updated_at = datetime.now(UTC)

    def calculate_score(self) -> int:
        """计算得分"""
        base_score = len(self.visited_nodes) * 10
        knowledge_bonus = len(self.knowledge_gained) * 50
        achievement_bonus = len(self.achievements) * 100
        hint_penalty = self.hints_used * 5

        self.score = max(0, base_score + knowledge_bonus + achievement_bonus - hint_penalty)
        return self.score
