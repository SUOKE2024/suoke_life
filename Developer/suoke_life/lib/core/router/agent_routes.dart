import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/presentation/home/screens/chat_screen.dart';

/// 智能体和聊天相关路由配置
class AgentRoutes {
  static const String chatPath = '/chat';
  
  /// 获取智能体相关路由配置
  static List<AutoRoute> get routes => [
    AutoRoute(
      path: chatPath,
      page: ChatRoute.page,
    ),
  ];
}