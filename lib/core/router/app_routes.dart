import 'package:auto_route/auto_route.dart';
import 'package:meta/meta.dart';

// 模拟路由页面定义 - 实际应用中这些路由会链接到真实的页面
// 这些通常由auto_route代码生成器自动生成

/// 主页路由
@internal
class HomeRoute {
  static const page = AutoRoutePage(path: '/home', name: 'HomeRoute');
}

/// 聊天标签页路由
@internal
class ChatTabRoute {
  static const page = AutoRoutePage(path: 'chat', name: 'ChatTabRoute');
}

/// SUOKE标签页路由
@internal
class SuokeTabRoute {
  static const page = AutoRoutePage(path: 'suoke', name: 'SuokeTabRoute');
}

/// 探索标签页路由
@internal
class ExploreTabRoute {
  static const page = AutoRoutePage(path: 'explore', name: 'ExploreTabRoute');
}

/// LIFE标签页路由
@internal
class LifeTabRoute {
  static const page = AutoRoutePage(path: 'life', name: 'LifeTabRoute');
}

/// 个人资料标签页路由
@internal
class ProfileTabRoute {
  static const page = AutoRoutePage(path: 'profile', name: 'ProfileTabRoute');
}

// 健康相关路由
@internal
class HealthRoute {
  static const page = AutoRoutePage(name: 'HealthRoute');
}

@internal
class HealthHomeRoute {
  static const page = AutoRoutePage(name: 'HealthHomeRoute');
}

@internal
class HealthAnalysisRoute {
  static const page = AutoRoutePage(name: 'HealthAnalysisRoute');
}

@internal
class HealthRecordsRoute {
  static const page = AutoRoutePage(name: 'HealthRecordsRoute');
}

// 知识图谱相关路由
@internal
class KnowledgeRoute {
  static const page = AutoRoutePage(name: 'KnowledgeRoute');
}

@internal
class KnowledgeHomeRoute {
  static const page = AutoRoutePage(name: 'KnowledgeHomeRoute');
}

@internal
class KnowledgeGraphRoute {
  static const page = AutoRoutePage(name: 'KnowledgeGraphRoute');
}

@internal
class KnowledgeDetailRoute {
  static const page = AutoRoutePage(name: 'KnowledgeDetailRoute');
}

// 新增知识图谱列表和详情页路由
@internal
class KnowledgeGraphListRoute {
  static const page = AutoRoutePage(name: 'KnowledgeGraphListRoute');
}

@internal
class KnowledgeGraphDetailRoute {
  static const page = AutoRoutePage(name: 'KnowledgeGraphDetailRoute');
}

// 身份验证相关路由
@internal
class LoginRoute {
  static const page = AutoRoutePage(name: 'LoginRoute');
}

@internal
class RegisterRoute {
  static const page = AutoRoutePage(name: 'RegisterRoute');
}

@internal
class ForgotPasswordRoute {
  static const page = AutoRoutePage(name: 'ForgotPasswordRoute');
}

// 模拟AutoRoutePage类 - 实际应用中这是由auto_route提供的
@internal
class AutoRoutePage {
  final String name;
  
  const AutoRoutePage({required this.name});
} 