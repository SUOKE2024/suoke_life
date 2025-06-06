"""
client - 索克生活项目模块
"""

    from api import corn_maze_pb2, corn_maze_pb2_grpc
from pathlib import Path
import argparse
import grpc
import sys
import uuid

#!/usr/bin/env python3

"""
Corn Maze Service 测试客户端

该客户端用于测试 Corn Maze Service 的功能，包括创建迷宫、移动、获取用户进度等。
"""



# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

# 导入生成的gRPC代码
try:
except ImportError:
    print("错误: 无法导入gRPC生成的Python代码, 请先运行生成脚本")
    sys.exit(1)


class CornMazeClient:
    """Corn Maze Service 测试客户端"""

    def __init__(self, host="localhost", port=50057, use_tls=False):
        """初始化客户端"""
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.use_tls = use_tls

        self._connect()

    def _connect(self):
        """连接到服务器"""
        target = f"{self.host}:{self.port}"

        if self.use_tls:
            # 使用SSL/TLS加密连接
            credentials = grpc.ssl_channel_credentials()
            self.channel = grpc.secure_channel(target, credentials)
        else:
            # 使用非加密连接
            self.channel = grpc.insecure_channel(target)

        self.stub = corn_maze_pb2_grpc.CornMazeServiceStub(self.channel)
        print(f"连接到 Corn Maze Service: {target}")

    def close(self):
        """关闭连接"""
        if self.channel:
            self.channel.close()
            print("连接已关闭")

    def create_maze(self, user_id=None, maze_type="四季养生", difficulty=2,
                   health_attributes=None, use_template=False, template_id=None):
        """创建迷宫"""
        if user_id is None:
            user_id = f"test_user_{uuid.uuid4()}"

        if health_attributes is None:
            health_attributes = {"体质": "气虚体质", "季节": "春季"}

        request = corn_maze_pb2.CreateMazeRequest(
            user_id=user_id,
            maze_type=maze_type,
            difficulty=difficulty,
            health_attributes=health_attributes,
            use_template=use_template
        )

        if use_template and template_id:
            request.template_id = template_id

        print(f"创建{maze_type}迷宫, 难度级别: {difficulty}...")
        try:
            response = self.stub.CreateMaze(request)
            print(f"迷宫创建成功! ID: {response.maze_id}")
            print(f"迷宫大小: {response.size_x}x{response.size_y}")
            print(f"知识点数量: {len(response.knowledge_nodes)}")
            print(f"挑战数量: {len(response.challenges)}")
            return response
        except grpc.RpcError as e:
            print(f"迷宫创建失败: {e.details()}")
            return None

        @cache(timeout=300)  # 5分钟缓存
def get_maze(self, maze_id, user_id):
        """获取迷宫信息"""
        request = corn_maze_pb2.GetMazeRequest(
            maze_id=maze_id,
            user_id=user_id
        )

        print(f"获取迷宫 {maze_id} 信息...")
        try:
            response = self.stub.GetMaze(request)
            print("迷宫信息获取成功!")
            print(f"迷宫类型: {response.maze_type}")
            print(f"迷宫大小: {response.size_x}x{response.size_y}")
            return response
        except grpc.RpcError as e:
            print(f"获取迷宫信息失败: {e.details()}")
            return None

    def move_in_maze(self, maze_id, user_id, direction):
        """在迷宫中移动"""
        # 将方向字符串映射到枚举值
        direction_map = {
            "north": corn_maze_pb2.NORTH,
            "east": corn_maze_pb2.EAST,
            "south": corn_maze_pb2.SOUTH,
            "west": corn_maze_pb2.WEST,
            "up": corn_maze_pb2.NORTH,
            "right": corn_maze_pb2.EAST,
            "down": corn_maze_pb2.SOUTH,
            "left": corn_maze_pb2.WEST,
            "n": corn_maze_pb2.NORTH,
            "e": corn_maze_pb2.EAST,
            "s": corn_maze_pb2.SOUTH,
            "w": corn_maze_pb2.WEST
        }

        # 获取方向枚举值
        dir_value = direction_map.get(direction.lower())
        if dir_value is None:
            print(f"无效的方向: {direction}")
            return None

        request = corn_maze_pb2.MoveRequest(
            maze_id=maze_id,
            user_id=user_id,
            direction=dir_value
        )

        print(f"在迷宫 {maze_id} 中向 {direction} 移动...")
        try:
            response = self.stub.MoveInMaze(request)
            if response.success:
                print(f"移动成功! 新位置: ({response.new_position.x}, {response.new_position.y})")
                if response.event_type != "NONE":
                    print(f"触发事件: {response.event_type}")
                    print(f"事件ID: {response.event_id}")
                    print(f"消息: {response.message}")
            else:
                print(f"移动失败: {response.message}")
            return response
        except grpc.RpcError as e:
            print(f"移动请求失败: {e.details()    @cache(timeout=300)  # 5分钟缓存
}")
            return None

    def get_user_progress(self, user_id, maze_id):
        """获取用户进度"""
        request = corn_maze_pb2.UserProgressRequest(
            user_id=user_id,
            maze_id=maze_id
        )

        print(f"获取用户 {user_id} 在迷宫 {maze_id} 中的进度...")
        try:
            response = self.stub.GetUserProgress(request)
            print("进度获取成功!")
            print(f"当前位置: ({response.current_position.x}, {response.current_position.y})")
            print(f"完成百分比: {response.completion_percentage}%")
            print(f"已访问单元格: {len(response.visited_cells)}")
            print(f"已完成挑战: {len(response.completed_challenges)}")
            print(f"已获取知识点: {len(response.acquired_knowledge)}")
            return response
        except grpc.RpcError as e:
            print(f"获取进度失败: {e.details()}")
            return None

    def list_maze_templates(self, maze_type="", difficulty=0, page=1, page_size=10):
        """列出迷宫模板"""
        request = corn_maze_pb2.ListMazeTemplatesRequest(
            maze_type=maze_type,
            difficulty=difficulty,
            page=page,
            page_size=page_size
        )

        filter_msg = []
        if maze_type:
            filter_msg.append(f"类型={maze_type}")
        if difficulty > 0:
            filter_msg.append(f"难度={difficulty}")

        filter_str = f"筛选条件: {', '.join(filter_msg)}" if filter_msg else "无筛选条件"
        print(f"获取迷宫模板列表 ({filter_str})...")

        try:
            response = self.stub.ListMazeTemplates(request)
            print(f"模板列表获取成功! 总数: {response.total}")

            for i, template in enumerate(response.templates, 1):
                print(f"\n模板 {i}:")
                print(f"  ID: {template.template_id}")
                print(f"  名称: {template.name}")
                print(f"  类型: {template.maze_type}")
                print(f"  难度: {template.difficulty}")
                print(f"  尺寸: {template.size_x}x{template.size_y}")

            return response
        except grpc.RpcError as e:
             @cache(timeout=300)  # 5分钟缓存
   print(f"获取模板列表失败: {e.details()}")
            return None

    def get_knowledge_node(self, node_id):
        """获取知识节点"""
        request = corn_maze_pb2.KnowledgeNodeRequest(
            node_id=node_id
        )

        print(f"获取知识节点 {node_id}...")
        try:
            response = self.stub.GetKnowledgeNode(request)
            print("知识节点获取成功!")
            print(f"标题: {response.node.title}")
            print(f"分类: {response.node.category}")
            print(f"难度级别: {response.node.difficulty_level}")
            print(f"内容: {response.node.content[:100]}...")  # 只显示前100个字符
            return response
        except grpc.RpcError as e:
            print(f"获取知识节点失败: {e.details()}")
            return None

    def record_maze_completion(self, user_id, maze_id, steps_taken=100,
                              time_spent_seconds=300, knowledge_nodes_discovered=5,
                              challenges_completed=3):
        """记录迷宫完成情况"""
        request = corn_maze_pb2.RecordMazeCompletionRequest(
            user_id=user_id,
            maze_id=maze_id,
            steps_taken=steps_taken,
            time_spent_seconds=time_spent_seconds,
            knowledge_nodes_discovered=knowledge_nodes_discovered,
            challenges_completed=challenges_completed
        )

        print(f"记录用户 {user_id} 完成迷宫 {maze_id}...")
        try:
            response = self.stub.RecordMazeCompletion(request)
            if response.success:
                print(f"记录成功! 完成ID: {response.completion_id}")
                print(f"获得积分: {response.points_earned}")

                if response.rewards:
                    print("获得奖励:")
                    for reward in response.rewards:
                        print(f"  - {reward.name}: {reward.description}")
            else:
                print(f"记录失败: {response.message}")
            return response
        except grpc.RpcError as e:
            print(f"记录完成情况失败: {e.details()}")
            return None


def demo_maze_exploration(client, user_id=None, steps=10):
    """演示迷宫探索流程"""
    if user_id is None:
        user_id = f"demo_user_{uuid.uuid4()}"

    print("\n=== 开始迷宫探索演示 ===\n")
    print(f"用户ID: {user_id}")

    # 创建迷宫
    maze = client.create_maze(
        user_id=user_id,
        maze_type="四季养生",
        difficulty=2,
        health_attributes={"体质": "气虚体质", "季节": "春季"}
    )

    if not maze:
        print("演示无法继续, 迷宫创建失败")
        return

    maze_id = maze.maze_id

    # 获取用户初始进度
    progress = client.get_user_progress(user_id, maze_id)

    if not progress:
        print("演示无法继续, 无法获取用户进度")
        return

    # 移动方向顺序
    directions = ["east", "south", "east", "north", "east", "south", "south", "west", "south", "east"]

    # 确保我们有足够的方向
    while len(directions) < steps:
        directions.extend(["east", "south", "west", "north"])

    # 只保留需要的步数
    directions = directions[:steps]

    # 开始移动
    print(f"\n开始移动 ({steps} 步):")

    for i, direction in enumerate(directions, 1):
        print(f"\n=== 步骤 {i}/{steps} ===")
        move_result = client.move_in_maze(maze_id, user_id, direction)

        if not move_result:
            print(f"步骤 {i} 失败, 演示中断")
            break

        # 如果遇到知识点，获取知识点详情
        if move_result.event_type == "KNOWLEDGE":
            client.get_knowledge_node(move_result.event_id)

    # 获取最终进度
    print("\n=== 最终进度 ===")
    client.get_user_progress(user_id, maze_id)

    # 记录迷宫完成情况
    print("\n=== 记录完成情况 ===")
    client.record_maze_completion(
        user_id=user_id,
        maze_id=maze_id,
        steps_taken=steps,
        time_spent_seconds=steps * 30,  # 假设每步花费30秒
        knowledge_nodes_discovered=2,
        challenges_completed=1
    )

    print("\n=== 演示结束 ===\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Corn Maze Service 测试客户端")
    parser.add_argument("--host", default="localhost", help="服务器主机名")
    parser.add_argument("--port", type=int, default=50057, help="服务器端口")
    parser.add_argument("--tls", action="store_true", help="使用TLS加密连接")
    parser.add_argument("--demo", action="store_true", help="运行演示模式")
    parser.add_argument("--steps", type=int, default=10, help="演示模式中的移动步数")

    args = parser.parse_args()

    client = CornMazeClient(host=args.host, port=args.port, use_tls=args.tls)

    try:
        if args.demo:
            demo_maze_exploration(client, steps=args.steps)
        else:
            _run_interactive_menu(client)
    finally:
        client.close()


def _run_interactive_menu(client):
    """运行交互式菜单"""
    menu_handlers = {
        "1": _handle_create_maze,
        "2": _handle_get_maze,
        "3": _handle_move_in_maze,
        "4": _handle_get_progress,
        "5": _handle_list_templates,
        "6": _handle_get_knowledge_node,
        "7": _handle_record_completion,
        "8": _handle_run_demo
    }

    while True:
        print("\n=== Corn Maze Service 测试客户端 ===")
        print("1. 创建迷宫")
        print("2. 获取迷宫信息")
        print("3. 在迷宫中移动")
        print("4. 获取用户进度")
        print("5. 列出迷宫模板")
        print("6. 获取知识节点")
        print("7. 记录迷宫完成情况")
        print("8. 运行演示")
        print("0. 退出")

        choice = input("\n请选择操作 (0-8): ")

        if choice == "0":
            break
        elif choice in menu_handlers:
            menu_handlers[choice](client)
        else:
            print("无效的选择, 请重试")


def _handle_create_maze(client):
    """处理创建迷宫"""
    user_id = input("用户ID (留空生成随机ID): ").strip() or None
    maze_type = input("迷宫类型 (默认: 四季养生): ").strip() or "四季养生"
    difficulty = int(input("难度级别 (1-5, 默认: 2): ").str    @cache(timeout=300)  # 5分钟缓存
ip() or "2")
    client.create_maze(user_id=user_id, maze_type=maze_type, difficulty=difficulty)


def _handle_get_maze(client):
    """处理获取迷宫信息"""
    maze_id = input("迷宫ID: ").strip()
    user_id = input("用户ID: ").strip()
    client.get_maze(maze_id, user_id)


def _handle_move_in_maze(client):
    """处理在迷宫中移动"""
    maze_id = input("迷宫ID: ").strip()
    user_id = input("用户    @cache(timeout=300)  # 5分钟缓存
ID: ").strip()
    direction = input("方向 (north/east/south/west): ").strip()
    client.move_in_maze(maze_id, user_id, direction)


def _handle_get_progress(client):
    """处理获取用户进度"""
    user_id = input("用户ID: ").strip()
    maze_id = input("迷宫ID: ").strip()
    client.get_user_progress(user_id, maze_id)


def _handle_list_templates(client):
    """处理列出迷宫模板"""
    maze_type = input(    @cache(timeout=300)  # 5分钟缓存
"迷宫类型 (留空表示所有): ").strip()
    difficulty = int(input("难度级别 (0表示所有): ").strip() or "0")
    client.list_maze_templates(maze_type=maze_type, difficulty=difficulty)


def _handle_get_knowledge_node(client):
    """处理获取知识节点"""
    node_id = input("知识节点ID: ").strip()
    client.get_knowledge_node(node_id)


def _handle_record_completion(client):
    """处理记录迷宫完成情况"""
    user_id = input("用户ID: ").strip()
    maze_id = input("迷宫ID: ").strip()
    steps = int(input("步数 (默认: 100): ").strip() or "100")
    time_spent = int(input("耗时(秒) (默认: 300): ").strip() or "300")
    client.record_maze_completion(user_id, maze_id, steps_taken=steps, time_spent_seconds=time_spent)


def _handle_run_demo(client):
    """处理运行演示"""
    user_id = input("用户ID (留空生成随机ID): ").strip() or None
    steps = int(input("步数 (默认: 10): ").strip() or "10")
    demo_maze_exploration(client, user_id=user_id, steps=steps)


if __name__ == "__main__":
    main()
