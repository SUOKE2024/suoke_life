import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/presentation/explore/screens/knowledge_graph_screen.dart';

/// 知识图谱相关路由配置
class KnowledgeRoutes {
  static const String knowledgeGraphPath = '/knowledge-graph';
  
  /// 获取知识图谱相关路由配置
  static List<AutoRoute> get routes => [
    AutoRoute(
      path: knowledgeGraphPath,
      page: KnowledgeGraphRoute.page,
    ),
  ];
}