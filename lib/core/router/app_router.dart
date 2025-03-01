import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../presentation/screens/splash/splash_screen.dart';
import '../../presentation/screens/welcome/welcome_screen.dart';
import '../../presentation/screens/auth/login_screen.dart';
import '../../presentation/screens/home/home_screen.dart';
import '../../presentation/screens/suoke/suoke_screen.dart';
import '../../presentation/screens/explore/explore_screen.dart';
import '../../presentation/screens/life/life_screen.dart';
import '../../presentation/screens/profile/profile_screen.dart';
import '../../presentation/screens/knowledge_graph/knowledge_graph_screen.dart';
import '../../presentation/screens/knowledge_graph/knowledge_graph_visualization_screen.dart';
import '../../presentation/screens/ai/rag_demo_screen.dart';
import '../../presentation/screens/knowledge_graph/knowledge_detail_screen.dart';
import '../../presentation/screens/appointment/appointment_list_screen.dart';
import '../../presentation/screens/appointment/appointment_detail_screen.dart';
import '../../presentation/screens/appointment/appointment_create_screen.dart';
import '../theme/app_colors.dart';
import 'route_observer.dart';

part 'app_router.gr.dart';
part 'app_router.g.dart';

/// 应用路由提供者
@riverpod
AppRouter appRouter(AppRouterRef ref) {
  return AppRouter();
}

/// 应用路由定义
@AutoRouterConfig()
class AppRouter extends _$AppRouter {
  @override
  List<AutoRoute> get routes => [
        // 启动页面
        AutoRoute(
          path: '/',
          page: SplashRoute.page,
          initial: true,
        ),
        
        // 欢迎页面
        AutoRoute(
          path: '/welcome',
          page: WelcomeRoute.page,
        ),
        
        // 认证相关路由
        AutoRoute(
          path: '/login',
          page: LoginRoute.page,
        ),
        
        // 主页面和底部导航
        AutoRoute(
          path: '/home',
          page: HomeRoute.page,
          children: [
            AutoRoute(
              path: 'chat',
              page: ChatTabRoute.page,
            ),
            AutoRoute(
              path: 'suoke',
              page: SuokeTabRoute.page,
            ),
            AutoRoute(
              path: 'explore',
              page: ExploreTabRoute.page,
            ),
            AutoRoute(
              path: 'life',
              page: LifeTabRoute.page,
            ),
            AutoRoute(
              path: 'profile',
              page: ProfileTabRoute.page,
            ),
          ],
        ),
        
        // 知识图谱相关路由
        AutoRoute(
          path: '/knowledge',
          page: KnowledgeGraphRoute.page,
        ),
        AutoRoute(
          path: '/knowledge-visualization',
          page: KnowledgeGraphVisualizationRoute.page,
        ),
        AutoRoute(
          path: '/knowledge-detail/:id',
          page: KnowledgeDetailRoute.page,
        ),
        
        // RAG演示
        AutoRoute(
          path: '/rag-demo',
          page: RagDemoRoute.page,
        ),
        
        // 预约相关路由
        AutoRoute(
          path: '/appointment',
          page: AppointmentListRoute.page,
        ),
        AutoRoute(
          path: '/appointment/detail/:id',
          page: AppointmentDetailRoute.page,
        ),
        AutoRoute(
          path: '/appointment/create',
          page: AppointmentCreateRoute.page,
        ),
      ];
      
  @override
  RouteType get defaultRouteType => RouteType.adaptive();
  
  @override
  List<NavigatorObserver> get navigatorObservers => [
    AppRouteObserver(),
  ];
}

/// 身份验证路由守卫
class AuthGuard extends AutoRouteGuard {
  final Ref ref;
  
  AuthGuard(this.ref);
  
  @override
  void onNavigation(NavigationResolver resolver, StackRouter router) {
    // 直接使用传入的ref获取身份验证状态，而不是创建新的ProviderContainer
    final authState = ref.read(authStateProvider);
    
    // 检查用户是否已登录
    if (authState.isAuthenticated) {
      // 如果已登录，允许导航继续
      resolver.next(true);
    } else {
      // 如果未登录，重定向到登录页面
      router.push(LoginRoute());
    }
  }
}

/// 主页面包装器 - 包含底部导航栏
@RoutePage()
class MainWrapperScreen extends ConsumerWidget {
  const MainWrapperScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return AutoTabsScaffold(
      routes: const [
        HomeRoute(),
        SuokeRoute(),
        ExploreRoute(),
        LifeRoute(),
        ProfileRoute(),
      ],
      bottomNavigationBuilder: (_, tabsRouter) {
        return Container(
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, -2),
              ),
            ],
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildNavItem(
                    context,
                    tabsRouter,
                    index: 0,
                    icon: Icons.home_outlined,
                    activeIcon: Icons.home,
                    label: '首页',
                  ),
                  _buildNavItem(
                    context,
                    tabsRouter,
                    index: 1,
                    icon: Icons.apps_outlined,
                    activeIcon: Icons.apps,
                    label: 'SUOKE',
                  ),
                  _buildNavItem(
                    context,
                    tabsRouter,
                    index: 2,
                    icon: Icons.explore_outlined,
                    activeIcon: Icons.explore,
                    label: '探索',
                  ),
                  _buildNavItem(
                    context,
                    tabsRouter,
                    index: 3,
                    icon: Icons.favorite_border,
                    activeIcon: Icons.favorite,
                    label: 'LIFE',
                  ),
                  _buildNavItem(
                    context,
                    tabsRouter,
                    index: 4,
                    icon: Icons.person_outline,
                    activeIcon: Icons.person,
                    label: '我的',
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
  
  /// 构建导航项
  Widget _buildNavItem(
    BuildContext context,
    TabsRouter tabsRouter, {
    required int index,
    required IconData icon,
    required IconData activeIcon,
    required String label,
  }) {
    final isSelected = tabsRouter.activeIndex == index;
    
    return GestureDetector(
      onTap: () => tabsRouter.setActiveIndex(index),
      behavior: HitTestBehavior.opaque,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isSelected ? activeIcon : icon,
              color: isSelected ? AppColors.primaryColor : Colors.grey,
              size: 24,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected ? AppColors.primaryColor : Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 全局身份验证状态提供者
final authStateProvider = Provider<AuthStateData>((ref) {
  return const AuthStateData(isAuthenticated: false);
});

/// 身份验证状态数据类
class AuthStateData {
  final bool isAuthenticated;
  
  const AuthStateData({required this.isAuthenticated});
} 