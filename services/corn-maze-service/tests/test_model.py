#!/usr/bin/env python3

"""
模型单元测试
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from corn_maze_service.internal.model.maze import (
    Maze,
    MazeDifficulty,
    MazeNode,
    MazeProgress,
    MazeTheme,
    NodeType,
    ProgressStatus,
    UserMaze,
)


class TestMazeModels:
    """迷宫模型测试类"""

    def test_maze_node_model(self):
        """测试迷宫节点模型"""
        node = MazeNode(
            x=1,
            y=2,
            node_type=NodeType.KNOWLEDGE,
            content={"title": "测试知识点", "description": "测试内容"},
            connections=[(0, 2), (2, 2)]
        )

        assert node.x == 1
        assert node.y == 2
        assert node.node_type == NodeType.KNOWLEDGE
        assert node.content["title"] == "测试知识点"
        assert not node.is_visited
        assert len(node.connections) == 2

    def test_maze_model_creation(self):
        """测试迷宫模型创建"""
        creator_id = uuid4()
        size = 5

        # 创建节点矩阵
        nodes = []
        for y in range(size):
            row = []
            for x in range(size):
                if x == 0 and y == 0:
                    node_type = NodeType.START
                elif x == size-1 and y == size-1:
                    node_type = NodeType.END
                else:
                    node_type = NodeType.PATH

                node = MazeNode(x=x, y=y, node_type=node_type)
                row.append(node)
            nodes.append(row)

        maze = Maze(
            name="测试迷宫",
            description="用于测试的迷宫",
            size=size,
            theme=MazeTheme.HEALTH,
            difficulty=MazeDifficulty.NORMAL,
            creator_id=creator_id,
            nodes=nodes,
            start_position=(0, 0),
            end_position=(size-1, size-1)
        )

        assert maze.name == "测试迷宫"
        assert maze.size == size
        assert maze.theme == MazeTheme.HEALTH
        assert maze.difficulty == MazeDifficulty.NORMAL
        assert maze.creator_id == creator_id
        assert maze.start_position == (0, 0)
        assert maze.end_position == (size-1, size-1)
        assert len(maze.nodes) == size
        assert len(maze.nodes[0]) == size

    def test_maze_model_validation(self):
        """测试迷宫模型验证"""
        creator_id = uuid4()

        # 测试无效的节点矩阵大小
        with pytest.raises(ValueError):
            Maze(
                name="测试迷宫",
                size=3,
                theme=MazeTheme.HEALTH,
                difficulty=MazeDifficulty.EASY,
                creator_id=creator_id,
                nodes=[[MazeNode(x=0, y=0, node_type=NodeType.START)]],  # 1x1 矩阵，但size=3
                start_position=(0, 0),
                end_position=(2, 2)
            )

        # 测试无效的位置坐标
        nodes = []
        for y in range(3):
            row = []
            for x in range(3):
                node = MazeNode(x=x, y=y, node_type=NodeType.PATH)
                row.append(node)
            nodes.append(row)

        with pytest.raises(ValueError):
            Maze(
                name="测试迷宫",
                size=3,
                theme=MazeTheme.HEALTH,
                difficulty=MazeDifficulty.EASY,
                creator_id=creator_id,
                nodes=nodes,
                start_position=(5, 5),  # 超出边界
                end_position=(2, 2)
            )

    def test_maze_node_operations(self):
        """测试迷宫节点操作"""
        creator_id = uuid4()
        size = 5  # 使用最小允许的大小

        # 创建节点矩阵
        nodes = []
        for y in range(size):
            row = []
            for x in range(size):
                node = MazeNode(x=x, y=y, node_type=NodeType.PATH)
                row.append(node)
            nodes.append(row)

        maze = Maze(
            name="测试迷宫",
            size=size,
            theme=MazeTheme.HEALTH,
            difficulty=MazeDifficulty.EASY,
            creator_id=creator_id,
            nodes=nodes,
            start_position=(0, 0),
            end_position=(size-1, size-1)
        )

        # 测试获取节点
        node = maze.get_node(1, 1)
        assert node is not None
        assert node.x == 1
        assert node.y == 1

        # 测试获取超出边界的节点
        node = maze.get_node(5, 5)
        assert node is None

        # 测试设置节点
        new_node = MazeNode(x=1, y=1, node_type=NodeType.KNOWLEDGE)
        maze.set_node(1, 1, new_node)
        retrieved_node = maze.get_node(1, 1)
        assert retrieved_node.node_type == NodeType.KNOWLEDGE

        # 测试获取相邻节点
        neighbors = maze.get_neighbors(2, 2)
        assert len(neighbors) == 4  # 中心位置有4个邻居

        # 测试边角位置的邻居
        corner_neighbors = maze.get_neighbors(0, 0)
        assert len(corner_neighbors) == 2  # 角落位置只有2个邻居

    def test_user_maze_model(self):
        """测试用户迷宫关联模型"""
        user_id = uuid4()
        maze_id = uuid4()

        user_maze = UserMaze(
            user_id=user_id,
            maze_id=maze_id,
            can_edit=True,
            can_share=True
        )

        assert user_maze.user_id == user_id
        assert user_maze.maze_id == maze_id
        assert user_maze.can_edit is True
        assert user_maze.can_share is True
        assert user_maze.last_accessed_at is None

    def test_maze_progress_model(self):
        """测试迷宫进度模型"""
        user_id = uuid4()
        maze_id = uuid4()

        progress = MazeProgress(
            user_id=user_id,
            maze_id=maze_id,
            current_position=(1, 2),
            visited_nodes=[(0, 0), (0, 1), (1, 1), (1, 2)],
            collected_items=["health_tip_1", "knowledge_point_2"]
        )

        assert progress.user_id == user_id
        assert progress.maze_id == maze_id
        assert progress.status == ProgressStatus.NOT_STARTED
        assert progress.current_position == (1, 2)
        assert len(progress.visited_nodes) == 4
        assert len(progress.collected_items) == 2
        assert progress.steps_count == 0
        assert progress.score == 0

        # 测试添加访问节点
        progress.add_visited_node(2, 2)
        assert len(progress.visited_nodes) == 5
        assert progress.steps_count == 1
        assert (2, 2) in progress.visited_nodes

        # 测试重复添加相同节点
        progress.add_visited_node(2, 2)
        assert len(progress.visited_nodes) == 5  # 不应该增加
        assert progress.steps_count == 1  # 步数也不应该增加

        # 测试完成迷宫
        progress.start_time = datetime.now(UTC)
        progress.complete_maze()
        assert progress.status == ProgressStatus.COMPLETED
        assert progress.end_time is not None
        assert progress.total_time is not None

        # 测试放弃迷宫
        progress2 = MazeProgress(
            user_id=user_id,
            maze_id=maze_id,
            current_position=(0, 0)
        )
        progress2.abandon_maze()
        assert progress2.status == ProgressStatus.ABANDONED

        # 测试计算得分
        progress.knowledge_gained = ["tip1", "tip2", "tip3"]
        progress.achievements = ["first_step", "explorer"]
        progress.hints_used = 2
        score = progress.calculate_score()

        # 基础分数 + 知识奖励 + 成就奖励 - 提示惩罚
        expected_score = len(progress.visited_nodes) * 10 + len(progress.knowledge_gained) * 50 + len(progress.achievements) * 100 - progress.hints_used * 5
        assert score == expected_score
        assert progress.score == expected_score

    def test_enum_values(self):
        """测试枚举值"""
        # 测试迷宫主题
        assert MazeTheme.HEALTH == "health"
        assert MazeTheme.NUTRITION == "nutrition"
        assert MazeTheme.TCM == "tcm"
        assert MazeTheme.BALANCE == "balance"

        # 测试迷宫难度
        assert MazeDifficulty.EASY == "easy"
        assert MazeDifficulty.NORMAL == "normal"
        assert MazeDifficulty.HARD == "hard"
        assert MazeDifficulty.EXPERT == "expert"

        # 测试节点类型
        assert NodeType.START == "start"
        assert NodeType.END == "end"
        assert NodeType.PATH == "path"
        assert NodeType.WALL == "wall"
        assert NodeType.KNOWLEDGE == "knowledge"
        assert NodeType.CHALLENGE == "challenge"
        assert NodeType.TREASURE == "treasure"

        # 测试进度状态
        assert ProgressStatus.NOT_STARTED == "not_started"
        assert ProgressStatus.IN_PROGRESS == "in_progress"
        assert ProgressStatus.COMPLETED == "completed"
        assert ProgressStatus.ABANDONED == "abandoned"
