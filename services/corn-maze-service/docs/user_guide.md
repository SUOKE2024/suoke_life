# Corn Maze Service 用户指南

本文档提供 Corn Maze Service 的用户指南，帮助开发者和集成商理解和使用此服务的功能。

## 目录

- [服务概述](#服务概述)
- [核心功能](#核心功能)
- [集成指南](#集成指南)
- [客户端示例](#客户端示例)
- [最佳实践](#最佳实践)
- [常见问题解答](#常见问题解答)
- [健康迷宫设计理念](#健康迷宫设计理念)

## 服务概述

Corn Maze Service 是 Soke Life APP 平台的一个微服务组件，负责生成和管理基于中医理论的"健康迷宫"体验。该服务将中医养生理念与游戏化体验相结合，为用户提供一种新颖的健康知识获取和实践方式。

### 服务特点

- **个性化迷宫**: 根据用户的健康状况和体质特点动态生成迷宫内容
- **中医知识融合**: 将中医养生知识自然地融入迷宫体验中
- **游戏化学习**: 通过迷宫探索和挑战激发用户学习中医养生知识的兴趣
- **进度追踪**: 记录用户的迷宫探索进度和成就
- **多种主题**: 支持四季养生、五行平衡、经络调理等多种主题迷宫

## 核心功能

### 1. 迷宫生成

服务可以生成多种类型的健康迷宫:

- **四季养生迷宫**: 根据春、夏、秋、冬四季特点设计的养生知识迷宫
- **五行平衡迷宫**: 基于金、木、水、火、土五行理论设计的养生迷宫
- **经络调理迷宫**: 围绕人体经络系统设计的养生迷宫

每种迷宫包含:
- 迷宫网格结构
- 知识节点 (提供养生知识)
- 挑战 (测试用户对知识的掌握)
- 奖励 (完成挑战后获得)

### 2. 迷宫交互

用户可以在迷宫中进行以下操作:

- 在迷宫中移动 (上、下、左、右)
- 查看遇到的知识点
- 完成挑战
- 获取奖励
- 追踪进度

### 3. 进度管理

服务会记录用户在迷宫中的进度:

- 当前位置
- 已访问的单元格
- 已获取的知识点
- 已完成的挑战
- 完成百分比
- 得分和成就

## 集成指南

### 系统要求

要集成 Corn Maze Service，您需要:

- 支持 gRPC 的开发环境
- 适当的身份验证和授权机制
- 能够处理和展示迷宫界面的前端组件

### 集成流程

1. **获取服务端点**

   向 Soke Life APP 平台管理员申请 Corn Maze Service 的服务端点和访问凭证。

2. **生成 gRPC 客户端代码**

   使用提供的 proto 文件生成您的开发语言对应的 gRPC 客户端代码。

   例如，对于 Python:
   ```bash
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. api/grpc/corn_maze.proto
   ```

3. **建立连接**

   使用服务端点和凭证建立与服务的安全连接。

4. **实现用户界面**

   开发迷宫显示、导航控制、知识点展示和挑战互动界面。

5. **管理用户会话**

   实现会话管理逻辑，包括保存和恢复用户在迷宫中的进度。

## 客户端示例

### Python 客户端示例

```python
import grpc
from api import corn_maze_pb2, corn_maze_pb2_grpc

# 创建安全通道
credentials = grpc.ssl_channel_credentials()
channel = grpc.secure_channel('cornmaze.example.com:443', credentials)
stub = corn_maze_pb2_grpc.CornMazeServiceStub(channel)

# 创建迷宫
def create_maze(user_id, maze_type="四季养生", difficulty=2):
    request = corn_maze_pb2.CreateMazeRequest(
        user_id=user_id,
        maze_type=maze_type,
        difficulty=difficulty,
        health_attributes={"体质": "气虚体质", "季节": "春季"}
    )
    
    response = stub.CreateMaze(request)
    return response

# 移动用户
def move_user(maze_id, user_id, direction):
    dir_map = {
        "up": corn_maze_pb2.NORTH,
        "right": corn_maze_pb2.EAST,
        "down": corn_maze_pb2.SOUTH,
        "left": corn_maze_pb2.WEST
    }
    
    request = corn_maze_pb2.MoveRequest(
        maze_id=maze_id,
        user_id=user_id,
        direction=dir_map[direction]
    )
    
    response = stub.MoveInMaze(request)
    return response

# 获取用户进度
def get_progress(user_id, maze_id):
    request = corn_maze_pb2.UserProgressRequest(
        user_id=user_id,
        maze_id=maze_id
    )
    
    response = stub.GetUserProgress(request)
    return response

# 示例使用流程
user_id = "user123"
maze = create_maze(user_id)
print(f"创建了迷宫: {maze.maze_id}")

# 移动用户
move_result = move_user(maze.maze_id, user_id, "right")
if move_result.success:
    print(f"移动成功，新位置: ({move_result.new_position.x}, {move_result.new_position.y})")
    if move_result.event_type == "KNOWLEDGE":
        print(f"发现知识点: {move_result.event_id}")
    elif move_result.event_type == "CHALLENGE":
        print(f"遇到挑战: {move_result.event_id}")
    elif move_result.event_type == "GOAL":
        print("到达终点！")
else:
    print(f"移动失败: {move_result.message}")

# 获取进度
progress = get_progress(user_id, maze.maze_id)
print(f"迷宫完成度: {progress.completion_percentage}%")
```

### 移动端集成示例

以下是在移动应用中集成迷宫服务的伪代码示例:

```dart
// Flutter示例
class MazeService {
  final CornMazeServiceClient _client;
  
  MazeService(String host, int port) {
    final channel = ClientChannel(
      host,
      port: port,
      options: ChannelOptions(
        credentials: ChannelCredentials.secure(),
      ),
    );
    _client = CornMazeServiceClient(channel);
  }
  
  Future<Maze> createMaze(String userId, String mazeType, int difficulty) async {
    final request = CreateMazeRequest()
      ..userId = userId
      ..mazeType = mazeType
      ..difficulty = difficulty;
      
    return await _client.createMaze(request);
  }
  
  Future<MoveResponse> moveInMaze(String mazeId, String userId, Direction direction) async {
    final request = MoveRequest()
      ..mazeId = mazeId
      ..userId = userId
      ..direction = direction;
      
    return await _client.moveInMaze(request);
  }
  
  // 其他方法...
}
```

## 最佳实践

### 迷宫渲染

1. **迷宫网格渲染**
   - 使用适合您平台的2D渲染技术
   - 只渲染用户视野范围内的单元格，提高性能
   - 为不同类型的单元格使用不同视觉效果

2. **用户界面设计**
   - 提供清晰的导航控制
   - 显示当前进度和位置
   - 设计吸引人的知识点和挑战展示界面

3. **离线支持**
   - 缓存已探索的迷宫数据
   - 支持无网络环境下继续探索已下载的迷宫
   - 在网络恢复后同步进度

### 性能优化

1. **批量获取**
   - 在初始化时获取整个迷宫结构
   - 预加载可能遇到的知识点和挑战

2. **异步操作**
   - 使用异步调用避免阻塞UI线程
   - 实现平滑的迷宫交互体验

3. **状态管理**
   - 有效管理用户在迷宫中的状态
   - 避免不必要的服务调用

## 常见问题解答

### 1. 迷宫大小是否有限制？

是的，默认情况下迷宫的最大尺寸为30x30。这个限制可以在服务配置中调整，但较大的迷宫可能会影响性能。

### 2. 如何处理用户网络断开的情况？

建议在客户端缓存迷宫结构和用户最新进度。当网络断开时，用户可以继续在缓存的迷宫中探索，等网络恢复后同步进度。

### 3. 如何自定义迷宫内容？

迷宫内容基于中医知识库自动生成。目前不支持完全自定义内容，但您可以通过提供特定的健康属性影响生成的内容类型。

### 4. 服务支持多语言吗？

目前服务主要支持中文内容。未来版本计划添加多语言支持。

### 5. 如何处理大量并发用户？

服务设计支持水平扩展。在高负载情况下，可以部署多个服务实例并使用负载均衡器分配请求。

## 健康迷宫设计理念

Corn Maze Service 的核心理念是通过游戏化方式传递中医养生知识，具体体现在以下几个方面：

### 四季养生迷宫

四季养生迷宫根据春、夏、秋、冬四季特点设计，每个季节迷宫有不同特色：

- **春季**：主题为"生发"，迷宫以绿色为主，知识点围绕春季养肝护肝、调整作息等内容
- **夏季**：主题为"生长"，迷宫以红色为主，知识点围绕夏季养心、防暑等内容
- **秋季**：主题为"收敛"，迷宫以金黄色为主，知识点围绕秋季养肺、润燥等内容
- **冬季**：主题为"藏伏"，迷宫以蓝黑色为主，知识点围绕冬季养肾、御寒等内容

### 五行平衡迷宫

五行平衡迷宫基于金、木、水、火、土五行理论，迷宫结构体现五行相生相克关系：

- 迷宫中五个区域分别对应五行
- 知识点涉及五行对应的脏腑、情绪、饮食等内容
- 挑战需要用户理解并应用五行平衡原理

### 经络调理迷宫

经络调理迷宫以人体十二正经和奇经八脉为基础设计：

- 迷宫路径模拟经络走向
- 知识点包括穴位功效、经络保健、拍打刮痧等内容
- 挑战包括穴位定位、经络辨识等互动内容

通过这些设计，Corn Maze Service 不仅提供了趣味性的游戏体验，更是将中医养生理念以适合现代人接受的方式进行了传递和应用。 