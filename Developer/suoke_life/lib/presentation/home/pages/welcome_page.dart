import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:suoke_life/core/storage/preferences_manager.dart';

/// 欢迎页面
@RoutePage()
class WelcomePage extends ConsumerStatefulWidget {
  const WelcomePage({super.key});

  @override
  ConsumerState<WelcomePage> createState() => _WelcomePageState();
}

class _WelcomePageState extends ConsumerState<WelcomePage>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _progressAnimation;
  late Animation<double> _logoScaleAnimation;
  late Animation<double> _pulsateAnimation;
  late Animation<double> _textFadeAnimation;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();

    print('欢迎页面初始化 - WelcomePage');

    // 动画控制器
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 5), // 恢复到5秒，不需要那么长
    );

    // 淡入动画
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.0, 0.3, curve: Curves.easeInOut),
      ),
    );

    // 进度条动画
    _progressAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.2, 0.9, curve: Curves.easeInOut),
      ),
    );

    // Logo缩放动画
    _logoScaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.0, 0.4, curve: Curves.easeOutBack),
      ),
    );

    // Logo脉动效果
    _pulsateAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.0, end: 1.05),
        weight: 1,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.05, end: 1.0),
        weight: 1,
      ),
    ]).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.5, 0.9, curve: Curves.easeInOut),
      ),
    );

    // 文字淡入动画
    _textFadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.3, 0.5, curve: Curves.easeInOut),
      ),
    );

    // 自动开始动画
    _animationController.forward();

    // 动画完成后只设置加载状态，不自动跳转
    _animationController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        setState(() {
          _isLoading = false;
        });
        // 移除自动跳转的代码，改为由用户通过按钮控制
        print('欢迎页面动画完成，等待用户点击按钮继续');
      }
    });
  }

  /// 根据登录状态导航到下一个页面
  void _navigateToNextScreen() async {
    print('开始导航到下一个页面 - WelcomePage');

    // 移除设置已看过欢迎页面的标记，确保每次启动都显示欢迎页面
    // final preferencesManager = ref.read(preferencesManagerProvider);
    // await preferencesManager.setHasSeenWelcome(true);

    // 检查用户是否已登录
    final authRepository = ref.read(authRepositoryProvider);
    print('用户登录状态: ${authRepository.isAuthenticated ? "已登录" : "未登录"}');

    if (authRepository.isAuthenticated) {
      // 已登录，直接导航到主页面，使用replaceAll确保导航堆栈干净
      if (mounted) {
        print('导航到主页面 - WelcomePage');
        context.router.replaceAll([const MainDashboardRoute()]);
      }
    } else {
      // 未登录，导航到登录页面
      if (mounted) {
        print('导航到登录页面 - WelcomePage');
        context.router.replace(LoginRoute());
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: Colors.white,
      // 使用SafeArea包装整个内容
      body: SafeArea(
        child: Stack(
          fit: StackFit.expand, // 确保Stack填充整个可用空间
          children: [
            // 背景图案
            Positioned.fill(
              child: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Colors.white,
                      AppColors.primaryColor.withAlpha(30),
                    ],
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                  ),
                ),
              ),
            ),

            // 图案装饰
            Positioned(
              right: -50,
              top: 100,
              child: Opacity(
                opacity: 0.1,
                child: Container(
                  width: 200,
                  height: 200,
                  decoration: BoxDecoration(
                    color: AppColors.primaryColor,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ),

            Positioned(
              left: -30,
              bottom: 200,
              child: Opacity(
                opacity: 0.1,
                child: Container(
                  width: 150,
                  height: 150,
                  decoration: BoxDecoration(
                    color: AppColors.secondaryColor,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ),

            // 欢迎内容 - 使用SizedBox约束确保有足够空间
            Center(
              child: SizedBox(
                width: screenSize.width * 0.8, // 限制宽度
                child: AnimatedBuilder(
                  animation: _animationController,
                  builder: (context, child) {
                    return Opacity(
                      opacity: _fadeAnimation.value,
                      child: Column(
                        mainAxisSize: MainAxisSize.min, // 避免无限高度
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          // Logo
                          Transform.scale(
                            scale: _logoScaleAnimation.value *
                                (_isLoading ? _pulsateAnimation.value : 1.0),
                            child: Container(
                              width: 140,
                              height: 140,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color:
                                        AppColors.primaryColor.withAlpha(100),
                                    blurRadius: 20,
                                    spreadRadius: 5,
                                  ),
                                ],
                                image: const DecorationImage(
                                  image:
                                      AssetImage('assets/images/app_icon.jpg'),
                                  fit: BoxFit.cover,
                                ),
                              ),
                            ),
                          ),

                          const SizedBox(height: 24),

                          // 应用名称
                          Opacity(
                            opacity: _textFadeAnimation.value,
                            child: const Text(
                              '索克生活',
                              style: TextStyle(
                                fontSize: 36,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 2,
                              ),
                            ),
                          ),

                          const SizedBox(height: 8),

                          // 应用口号
                          Opacity(
                            opacity: _textFadeAnimation.value,
                            child: Text(
                              '智慧生活 · 健康养生',
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey.withAlpha(180),
                                letterSpacing: 1,
                              ),
                            ),
                          ),

                          const SizedBox(height: 60),

                          // 加载进度条
                          SizedBox(
                            width: screenSize.width * 0.6,
                            child: LinearProgressIndicator(
                              value: _progressAnimation.value,
                              backgroundColor: Colors.grey.withAlpha(50),
                              color: AppColors.primaryColor,
                              minHeight: 6,
                              borderRadius: BorderRadius.circular(3),
                            ),
                          ),

                          const SizedBox(height: 16),

                          // 加载状态文本
                          Text(
                            _isLoading ? '正在加载中...' : '加载完成',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.withAlpha(150),
                            ),
                          ),

                          // 增加一个明显的进入按钮
                          if (!_isLoading) ...[
                            const SizedBox(height: 30),
                            ElevatedButton(
                              onPressed: _navigateToNextScreen,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppColors.primaryColor,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 40, vertical: 15),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(30),
                                ),
                              ),
                              child: const Text(
                                '点击进入',
                                style: TextStyle(
                                    fontSize: 18, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ],
                        ],
                      ),
                    );
                  },
                ),
              ),
            ),

            // 版本信息
            Positioned(
              bottom: 24,
              left: 0,
              right: 0,
              child: Center(
                child: Text(
                  'V1.0.0',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.withAlpha(150),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
