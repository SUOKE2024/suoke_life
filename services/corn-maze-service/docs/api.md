# Corn Maze Service API 文档

本文档详细说明了 Corn Maze Service 提供的所有API接口。

## 目录

- [概述](#概述)
- [gRPC 接口](#grpc-接口)
  - [CreateMaze](#createmaze)
  - [GetMaze](#getmaze)
  - [MoveInMaze](#moveinmaze)
  - [GetUserProgress](#getuserprogress)
  - [ListMazeTemplates](#listmazetemplates)
  - [RecordMazeCompletion](#recordmazecompletion)
  - [GetKnowledgeNode](#getknowledgenode)
- [数据模型](#数据模型)
- [错误处理](#错误处理)
- [示例代码](#示例代码)

## 概述

Corn Maze Service 提供基于 gRPC 的接口，用于创建、管理和交互迷宫体验。所有接口都定义在 `api/grpc/corn_maze.proto` 文件中。

## gRPC 接口

### CreateMaze

创建一个新的迷宫实例。

**请求**:
```protobuf
message CreateMazeRequest {
  string user_id = 1;              // 用户ID
  string maze_type = 2;            // 迷宫类型：四季养生、五行平衡、经络调理等
  int32 difficulty = 3;            // 难度级别：1-5
  map<string, string> health_attributes = 4;  // 用户健康属性
  bool use_template = 5;           // 是否使用模板
  string template_id = 6;          // 模板ID（如果使用模板）
}
```

**响应**:
```protobuf
message MazeResponse {
  string maze_id = 1;              // 迷宫ID
  string maze_type = 2;            // 迷宫类型
  int32 size_x = 3;                // 宽度
  int32 size_y = 4;                // 高度
  repeated MazeCell cells = 5;     // 迷宫单元格
  Position start_position = 6;     // 起点位置
  Position goal_position = 7;      // 终点位置
  repeated KnowledgeNode knowledge_nodes = 8;  // 知识节点
  repeated Challenge challenges = 9;  // 挑战
  string created_at = 10;          // 创建时间
  int32 difficulty = 11;           // 难度级别
  string status = 12;              // 状态
}
```

**使用场景**:
- 用户首次进入迷宫体验
- 根据用户健康状况创建个性化迷宫

**注意事项**:
- 迷宫生成可能需要一些时间，特别是大型迷宫
- 健康属性对迷宫内容有显著影响

### GetMaze

获取已存在迷宫的详细信息。

**请求**:
```protobuf
message GetMazeRequest {
  string maze_id = 1;              // 迷宫ID
  string user_id = 2;              // 用户ID
}
```

**响应**:
与 CreateMaze 相同的 MazeResponse 消息。

**使用场景**:
- 用户重新进入之前创建的迷宫
- 获取迷宫详细信息进行展示

### MoveInMaze

在迷宫中移动用户位置。

**请求**:
```protobuf
message MoveRequest {
  string maze_id = 1;              // 迷宫ID
  string user_id = 2;              // 用户ID
  Direction direction = 3;         // 移动方向
}

enum Direction {
  NORTH = 0;
  EAST = 1;
  SOUTH = 2;
  WEST = 3;
}
```

**响应**:
```protobuf
message MoveResponse {
  bool success = 1;                // 是否移动成功
  Position new_position = 2;       // 新位置
  string event_type = 3;           // 事件类型
  string event_id = 4;             // 事件ID
  string message = 5;              // 消息
}
```

**使用场景**:
- 用户在迷宫中导航
- 触发迷宫中的事件（如知识点、挑战）

**可能的事件类型**:
- `NONE`: 无事件
- `KNOWLEDGE`: 遇到知识点
- `CHALLENGE`: 遇到挑战
- `GOAL`: 到达终点

### GetUserProgress

获取用户在迷宫中的进度信息。

**请求**:
```protobuf
message UserProgressRequest {
  string user_id = 1;              // 用户ID
  string maze_id = 2;              // 迷宫ID
}
```

**响应**:
```protobuf
message UserProgressResponse {
  string user_id = 1;              // 用户ID
  string maze_id = 2;              // 迷宫ID
  Position current_position = 3;   // 当前位置
  repeated string visited_cells = 4;  // 已访问单元格
  repeated string completed_challenges = 5;  // 已完成挑战
  repeated string acquired_knowledge = 6;  // 已获取知识点
  int32 completion_percentage = 7;  // 完成百分比
  string status = 8;               // 状态
  int32 steps_taken = 9;           // 已走步数
  string start_time = 10;          // 开始时间
  string last_active_time = 11;    // 最后活动时间
}
```

**使用场景**:
- 显示用户当前进度
- 分析用户体验情况
- 恢复用户迷宫会话

### ListMazeTemplates

获取可用的迷宫模板列表。

**请求**:
```protobuf
message ListMazeTemplatesRequest {
  string maze_type = 1;            // 迷宫类型筛选
  int32 difficulty = 2;            // 难度级别筛选
  int32 page = 3;                  // 页码
  int32 page_size = 4;             // 每页大小
}
```

**响应**:
```protobuf
message ListMazeTemplatesResponse {
  repeated MazeTemplate templates = 1;  // 模板列表
  int32 total = 2;                 // 总数
}

message MazeTemplate {
  string template_id = 1;          // 模板ID
  string name = 2;                 // 名称
  string description = 3;          // 描述
  string maze_type = 4;            // 迷宫类型
  int32 difficulty = 5;            // 难度级别
  string preview_image_url = 6;    // 预览图
  int32 size_x = 7;                // 宽度
  int32 size_y = 8;                // 高度
  int32 knowledge_node_count = 9;  // 知识点数量
  int32 challenge_count = 10;      // 挑战数量
}
```

**使用场景**:
- 让用户选择迷宫模板
- 浏览不同类型和难度的迷宫

### RecordMazeCompletion

记录用户完成迷宫的情况。

**请求**:
```protobuf
message RecordMazeCompletionRequest {
  string user_id = 1;              // 用户ID
  string maze_id = 2;              // 迷宫ID
  int32 steps_taken = 3;           // 步数
  int32 time_spent_seconds = 4;    // 耗时(秒)
  int32 knowledge_nodes_discovered = 5;  // 发现的知识点数量
  int32 challenges_completed = 6;  // 完成的挑战数量
}
```

**响应**:
```protobuf
message RecordMazeCompletionResponse {
  bool success = 1;                // 是否成功
  string completion_id = 2;        // 完成记录ID
  int32 points_earned = 3;         // 获得的积分
  repeated Reward rewards = 4;     // 奖励
  string message = 5;              // 消息
}

message Reward {
  string reward_id = 1;            // 奖励ID
  string reward_type = 2;          // 奖励类型
  string name = 3;                 // 名称
  string description = 4;          // 描述
  int32 value = 5;                 // 值
}
```

**使用场景**:
- 用户完成迷宫后的奖励发放
- 记录用户的迷宫完成情况
- 计算用户得分和成就

### GetKnowledgeNode

获取特定知识节点的详细信息。

**请求**:
```protobuf
message KnowledgeNodeRequest {
  string node_id = 1;              // 节点ID
}
```

**响应**:
```protobuf
message KnowledgeNodeResponse {
  KnowledgeNode node = 1;          // 知识节点
}

message KnowledgeNode {
  string node_id = 1;              // 节点ID
  string title = 2;                // 标题
  string content = 3;              // 内容
  string category = 4;             // 分类
  string difficulty_level = 5;     // 难度级别
  repeated string related_tags = 6;  // 相关标签
}
```

**使用场景**:
- 用户查看遇到的知识点详情
- 知识点详情页面展示

## 数据模型

### MazeCell

定义迷宫的单个单元格。

```protobuf
message MazeCell {
  int32 x = 1;                     // X坐标
  int32 y = 2;                     // Y坐标
  CellType type = 3;               // 单元格类型
  bool north_wall = 4;             // 北墙
  bool east_wall = 5;              // 东墙
  bool south_wall = 6;             // 南墙
  bool west_wall = 7;              // 西墙
  string cell_id = 8;              // 单元格ID
  string content_id = 9;           // 内容ID
}

enum CellType {
  EMPTY = 0;                       // 空
  PATH = 1;                        // 路径
  WALL = 2;                        // 墙
  START = 3;                       // 起点
  GOAL = 4;                        // 终点
  KNOWLEDGE = 5;                   // 知识点
  CHALLENGE = 6;                   // 挑战
  REWARD = 7;                      // 奖励
}
```

### Position

表示迷宫中的位置。

```protobuf
message Position {
  int32 x = 1;                     // X坐标
  int32 y = 2;                     // Y坐标
}
```

### Challenge

表示迷宫中的挑战。

```protobuf
message Challenge {
  string challenge_id = 1;         // 挑战ID
  string title = 2;                // 标题
  string description = 3;          // 描述
  string type = 4;                 // 类型
  string difficulty_level = 5;     // 难度级别
  string reward_description = 6;   // 奖励描述
}
```

## 错误处理

以下是可能返回的错误代码及其含义:

| 错误码 | 描述 |
|-------|------|
| INVALID_ARGUMENT | 请求参数无效 |
| NOT_FOUND | 请求的资源不存在 |
| PERMISSION_DENIED | 用户无权访问请求的资源 |
| INTERNAL | 服务器内部错误 |
| UNAVAILABLE | 服务暂时不可用 |

## 示例代码

### Python 客户端示例

```python
import grpc
from api import corn_maze_pb2, corn_maze_pb2_grpc

# 创建通道
channel = grpc.insecure_channel('localhost:50057')
stub = corn_maze_pb2_grpc.CornMazeServiceStub(channel)

# 创建迷宫
create_request = corn_maze_pb2.CreateMazeRequest(
    user_id="user123",
    maze_type="四季养生",
    difficulty=2,
    health_attributes={"体质": "气虚体质"},
    use_template=False
)
maze_response = stub.CreateMaze(create_request)
print(f"创建的迷宫ID: {maze_response.maze_id}")

# 在迷宫中移动
move_request = corn_maze_pb2.MoveRequest(
    maze_id=maze_response.maze_id,
    user_id="user123",
    direction=corn_maze_pb2.NORTH
)
move_response = stub.MoveInMaze(move_request)
print(f"移动结果: {'成功' if move_response.success else '失败'}")
print(f"新位置: ({move_response.new_position.x}, {move_response.new_position.y})") 