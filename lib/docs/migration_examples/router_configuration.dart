import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// 步骤1: 定义应用的路由
@AutoRouterConfig()
class AppRouter extends $AppRouter {
  @override
  List<AutoRoute> get routes => [
    // 在这里定义你的路由
    AutoRoute(page: HomeRoute.page, initial: true),
    AutoRoute(page: ExploreRoute.page),
    AutoRoute(page: LifeRoute.page),
    AutoRoute(page: SuokeRoute.page),
    AutoRoute(page: ProfileRoute.page),
    AutoRoute(page: ChatRoute.page),
    
    // 健康相关路由
    AutoRoute(
      page: HealthRoute.page,
      children: [
        AutoRoute(page: HealthHomeRoute.page, initial: true),
        AutoRoute(page: HealthAnalysisRoute.page),
        AutoRoute(page: HealthRecordsRoute.page),
      ],
    ),
    
    // 登录和注册路由
    AutoRoute(page: LoginRoute.page),
    AutoRoute(page: RegisterRoute.page),
  ];
}

// 步骤2: 创建路由页面定义
// 主页
@RoutePage()
class HomePage extends StatelessWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('Home Page')),
    );
  }
}

// 探索页
@RoutePage()
class ExplorePage extends StatelessWidget {
  const ExplorePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('Explore Page')),
    );
  }
}

// 生活页
@RoutePage()
class LifePage extends StatelessWidget {
  const LifePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('Life Page')),
    );
  }
}

// ... 其他页面定义

// 步骤3: 创建认证状态管理
// 用户认证状态
class AuthState {
  final bool isAuthenticated;
  final User? user;

  AuthState({this.isAuthenticated = false, this.user});
}

class User {
  final String id;
  final String name;
  final String? email;

  User({required this.id, required this.name, this.email});
}

// 认证状态Notifier
class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState());

  Future<void> login(String username, String password) async {
    // 模拟登录API调用
    await Future.delayed(const Duration(seconds: 1));
    state = AuthState(
      isAuthenticated: true,
      user: User(id: '1', name: username, email: '$username@example.com'),
    );
  }

  void logout() {
    state = AuthState();
  }
}

// 认证状态Provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});

// 步骤4: 创建路由守卫
// 认证路由守卫Middleware
class AuthGuard extends AutoRouteGuard {
  final AuthState authState;

  AuthGuard(this.authState);

  @override
  void onNavigation(NavigationResolver resolver, StackRouter router) {
    if (authState.isAuthenticated) {
      // 用户已认证，允许导航
      resolver.next(true);
    } else {
      // 用户未认证，重定向到登录页
      router.push(LoginRoute());
    }
  }
}

// 步骤5: 集成Riverpod和auto_route
// 路由Provider
final appRouterProvider = Provider<AppRouter>((ref) {
  final authState = ref.watch(authProvider);
  return AppRouter(authGuard: AuthGuard(authState));
});

// 步骤6: 在主应用中使用
/*
class MyApp extends ConsumerWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 获取路由实例
    final appRouter = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: '索克生活',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      routerDelegate: appRouter.delegate(),
      routeInformationParser: appRouter.defaultRouteParser(),
    );
  }
}
*/

// 步骤7: 使用示例 - 在其他Widget中进行导航
/*
class NavigationExample extends ConsumerWidget {
  const NavigationExample({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      children: [
        ElevatedButton(
          onPressed: () {
            // 使用context.router进行导航
            context.router.push(const HealthRoute());
          },
          child: const Text('跳转到健康页面'),
        ),
        ElevatedButton(
          onPressed: () {
            // 使用自动生成的路由方法
            context.router.navigate(const SuokeRoute());
          },
          child: const Text('跳转到SUOKE页面'),
        ),
        ElevatedButton(
          onPressed: () {
            // 登出并重定向
            ref.read(authProvider.notifier).logout();
            context.router.replaceAll([const LoginRoute()]);
          },
          child: const Text('登出'),
        ),
      ],
    );
  }
}
*/

// 模拟生成的路由代码
abstract class $AppRouter {}

// 模拟路由页面
class HomeRoute {
  static const page = AutoRoutePage(name: 'HomeRoute');
}

class ExploreRoute {
  static const page = AutoRoutePage(name: 'ExploreRoute');
}

class LifeRoute {
  static const page = AutoRoutePage(name: 'LifeRoute');
}

class SuokeRoute {
  static const page = AutoRoutePage(name: 'SuokeRoute');
}

class ProfileRoute {
  static const page = AutoRoutePage(name: 'ProfileRoute');
}

class ChatRoute {
  static const page = AutoRoutePage(name: 'ChatRoute');
}

class HealthRoute {
  static const page = AutoRoutePage(name: 'HealthRoute');
}

class HealthHomeRoute {
  static const page = AutoRoutePage(name: 'HealthHomeRoute');
}

class HealthAnalysisRoute {
  static const page = AutoRoutePage(name: 'HealthAnalysisRoute');
}

class HealthRecordsRoute {
  static const page = AutoRoutePage(name: 'HealthRecordsRoute');
}

class LoginRoute {
  static const page = AutoRoutePage(name: 'LoginRoute');
}

class RegisterRoute {
  static const page = AutoRoutePage(name: 'RegisterRoute');
}

// 模拟AutoRoutePage类
class AutoRoutePage {
  final String name;
  const AutoRoutePage({required this.name});
} 