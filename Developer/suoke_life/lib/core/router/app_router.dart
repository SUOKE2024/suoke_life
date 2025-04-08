import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// 页面导入
import 'package:suoke_life/presentation/home/pages/home_page.dart';
import 'package:suoke_life/presentation/home/pages/chat_page.dart';
import 'package:suoke_life/presentation/home/screens/chat_screen.dart';
import 'package:suoke_life/presentation/suoke/pages/suoke_page.dart';
import 'package:suoke_life/presentation/suoke/pages/pulse_diagnosis_page.dart';
import 'package:suoke_life/presentation/suoke/pages/tongue_diagnosis_page.dart';
import 'package:suoke_life/presentation/tcm/tcm_diagnosis_page.dart';
import 'package:suoke_life/presentation/explore/pages/explore_page.dart';
import 'package:suoke_life/presentation/explore/pages/exploration_detail_page.dart';
import 'package:suoke_life/presentation/explore/pages/knowledge_article_detail_page.dart';
import 'package:suoke_life/presentation/explore/screens/knowledge_graph_screen.dart';
import 'package:suoke_life/presentation/life/pages/life_page.dart';
import 'package:suoke_life/presentation/profile/pages/profile_page.dart';
import 'package:suoke_life/presentation/home/pages/welcome_page.dart';
import 'package:suoke_life/presentation/auth/pages/login_page.dart';
import 'package:suoke_life/presentation/explore/providers/explore_providers.dart';
import 'package:suoke_life/presentation/life/pages/constitution_assessment_page.dart';
import 'package:suoke_life/presentation/life/pages/constitution_result_page.dart';
import 'package:suoke_life/presentation/life/pages/health_regimen_page.dart';
import 'package:suoke_life/presentation/profile/pages/theme_settings_page.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/presentation/life/models/constitution_type.dart';
import 'package:suoke_life/presentation/sensing/sensing_control_page.dart';
import 'package:suoke_life/presentation/life/health_profile_page.dart';
import 'package:suoke_life/presentation/explore/rag_search_page.dart';
import 'package:suoke_life/presentation/auth/pages/register_page.dart';
import 'package:suoke_life/presentation/auth/pages/two_factor_auth_page.dart';
import 'package:suoke_life/presentation/auth/pages/biometric_auth_page.dart';
import 'package:suoke_life/presentation/network_test/network_test_screen.dart';
import 'package:suoke_life/presentation/home/api_test_page.dart';
import 'package:suoke_life/presentation/blockchain/blockchain_page.dart';
import 'package:suoke_life/presentation/blockchain/health_record_detail_page.dart';
import 'package:suoke_life/presentation/blockchain/wallet_page.dart';
import 'package:suoke_life/presentation/blockchain/health_record_page.dart';
import 'package:suoke_life/presentation/splash/splash_page.dart';

// 路由配置
import 'package:suoke_life/core/router/agent_routes.dart';
import 'package:suoke_life/core/router/knowledge_routes.dart';
import 'package:suoke_life/core/router/tcm_routes.dart';
import 'package:suoke_life/core/router/blockchain_routes.dart';

part 'app_router.gr.dart';

/// 路由提供者
final appRouterProvider = Provider<AppRouter>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  return AppRouter(authGuard: AuthGuard(authRepository));
});

/// 应用程序路由配置
@AutoRouterConfig(replaceInRouteName: 'Page,Route,Screen,Route')
class AppRouter extends $AppRouter {
  final AuthGuard authGuard;

  AppRouter({required this.authGuard});

  @override
  List<AutoRoute> get routes => [
    // 闪屏页
    AutoRoute(page: SplashRoute.page, initial: true),
    
    // 认证相关页面
    AutoRoute(page: LoginRoute.page),
    AutoRoute(page: RegisterRoute.page),
    
    // 主页
    AutoRoute(
      page: HomeRoute.page,
      guards: [authGuard],
    ),
    
    // 个人资料页
    AutoRoute(
      page: ProfileRoute.page,
      guards: [authGuard],
    ),
    
    // 区块链页面
    AutoRoute(
      page: BlockchainRoute.page,
      guards: [authGuard],
    ),
    
    // 知识文章详情页面
    AutoRoute(
      path: '/knowledge/articles/:articleId',
      page: KnowledgeArticleDetailRoute.page,
    ),
    
    // 引入其他路由配置
    ...AgentRoutes.routes,
    ...KnowledgeRoutes.routes,
    ...TcmRoutes.routes,
    ...BlockchainRoutes.routes,
    
    // 新增路由
    AutoRoute(
      path: '/chat',
      page: ChatRoute.page,
    ),
    AutoRoute(
      path: '/knowledge-graph',
      page: KnowledgeGraphRoute.page,
    ),
    // 可添加其他路由
  ];
}

/// 身份验证路由守卫
class AuthGuard extends AutoRouteGuard {
  final AuthRepository authRepository;

  AuthGuard(this.authRepository);

  @override
  void onNavigation(NavigationResolver resolver, StackRouter router) async {
    final isAuthenticated = await authRepository.isAuthenticated();
    
    if (isAuthenticated) {
      resolver.next(true);
    } else {
      router.push(LoginRoute());
    }
  }
}

/// 主仪表盘页面，包含底部导航栏
@RoutePage()
class MainDashboardPage extends StatelessWidget {
  const MainDashboardPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AutoTabsRouter(
      routes: const [
        HomeRoute(),
        SuokeRoute(),
        ExploreRoute(),
        LifeRoute(),
        ProfileRoute(),
      ],
      builder: (context, child) {
        final tabsRouter = AutoTabsRouter.of(context);

        return Scaffold(
          body: child,
          bottomNavigationBar: _buildBottomNavigationBar(context, tabsRouter),
        );
      },
    );
  }

  /// 构建底部导航栏
  Widget _buildBottomNavigationBar(
      BuildContext context, TabsRouter tabsRouter) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(10),
            blurRadius: 4,
            offset: const Offset(0, -1),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        child: BottomNavigationBar(
          currentIndex: tabsRouter.activeIndex,
          onTap: tabsRouter.setActiveIndex,
          backgroundColor:
              isDarkMode ? AppColors.darkSurface : AppColors.lightSurface,
          selectedItemColor: AppColors.primaryColor,
          unselectedItemColor:
              isDarkMode ? AppColors.darkSystemGray : AppColors.lightSystemGray,
          type: BottomNavigationBarType.fixed,
          elevation: 0,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.chat_bubble_outline),
              activeIcon: Icon(Icons.chat_bubble),
              label: '首页',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.health_and_safety_outlined),
              activeIcon: Icon(Icons.health_and_safety),
              label: 'SUOKE',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.explore_outlined),
              activeIcon: Icon(Icons.explore),
              label: '探索',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.spa_outlined),
              activeIcon: Icon(Icons.spa),
              label: 'LIFE',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline),
              activeIcon: Icon(Icons.person),
              label: '我的',
            ),
          ],
        ),
      ),
    );
  }
}

/// 404 页面定义
@RoutePage()
class NotFoundPage extends StatelessWidget {
  const NotFoundPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('页面未找到'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red,
            ),
            const SizedBox(height: 16),
            const Text(
              '404 - 页面未找到',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              '您请求的页面不存在',
              style: TextStyle(
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                // 导航到主仪表盘页面
                context.router.navigate(const MainDashboardRoute());
              },
              child: const Text('返回首页'),
            ),
          ],
        ),
      ),
    );
  }
}

/// 网络测试页面路由
@RoutePage()
class NetworkTestRoute extends StatelessWidget {
  const NetworkTestRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return const NetworkTestScreen();
  }
}
