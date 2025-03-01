import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lottie/lottie.dart';

import '../../../core/theme/app_colors.dart';
import '../../routes/app_router.dart';

/// 欢迎页面
///
/// 应用程序启动时的首个页面，显示logo和加载动画
@RoutePage()
class WelcomeScreen extends ConsumerStatefulWidget {
  const WelcomeScreen({super.key});

  @override
  ConsumerState<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends ConsumerState<WelcomeScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeInAnimation;
  late Animation<double> _progressAnimation;
  
  bool _isLoading = true;
  bool _hasError = false;
  String _errorMessage = '';
  
  @override
  void initState() {
    super.initState();
    
    // 设置动画控制器
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    );
    
    // 设置淡入动画
    _fadeInAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.0, 0.5, curve: Curves.easeIn),
      ),
    );
    
    // 设置进度条动画
    _progressAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.2, 0.9, curve: Curves.easeInOut),
      ),
    );
    
    // 动画监听器
    _animationController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _navigateToNextScreen();
      }
    });
    
    // 开始加载
    _loadAppData();
  }
  
  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }
  
  /// 加载应用数据
  Future<void> _loadAppData() async {
    try {
      // 模拟数据加载过程
      await Future.delayed(const Duration(seconds: 2));
      
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        
        // 启动动画
        _animationController.forward();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _hasError = true;
          _errorMessage = '加载失败，请稍后重试';
          _isLoading = false;
        });
      }
    }
  }
  
  /// 重试加载
  void _retry() {
    setState(() {
      _isLoading = true;
      _hasError = false;
      _errorMessage = '';
    });
    
    _loadAppData();
  }
  
  /// 导航到下一个页面
  void _navigateToNextScreen() {
    // 判断用户是否已登录，决定导航到登录页面还是主页
    final isLoggedIn = false; // 实际应用中，这里会从存储中检查登录状态
    
    if (isLoggedIn) {
      context.router.replace(const MainWrapperRoute());
    } else {
      context.router.replace(const LoginRoute());
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: Center(
        child: _hasError
            ? _buildErrorWidget()
            : _buildLoadingWidget(),
      ),
    );
  }
  
  /// 构建加载小部件
  Widget _buildLoadingWidget() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Logo
        AnimatedBuilder(
          animation: _fadeInAnimation,
          builder: (context, child) {
            return Opacity(
              opacity: _fadeInAnimation.value,
              child: child,
            );
          },
          child: Container(
            width: 150,
            height: 150,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.primaryColor,
            ),
            child: const Icon(
              Icons.spa, // 临时使用的图标，实际应用中应替换为应用Logo
              color: Colors.white,
              size: 80,
            ),
          ),
        ),
        
        const SizedBox(height: 32),
        
        // 应用名称
        AnimatedBuilder(
          animation: _fadeInAnimation,
          builder: (context, child) {
            return Opacity(
              opacity: _fadeInAnimation.value,
              child: child,
            );
          },
          child: Text(
            '索克生活',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              color: AppColors.primaryColor,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        
        const SizedBox(height: 40),
        
        // 进度条
        if (!_isLoading)
          AnimatedBuilder(
            animation: _progressAnimation,
            builder: (context, child) {
              return SizedBox(
                width: MediaQuery.of(context).size.width * 0.6,
                child: LinearProgressIndicator(
                  value: _progressAnimation.value,
                  backgroundColor: Colors.grey.shade300,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    AppColors.primaryColor,
                  ),
                  minHeight: 4,
                ),
              );
            },
          ),
        
        if (_isLoading)
          SizedBox(
            width: MediaQuery.of(context).size.width * 0.6,
            child: LinearProgressIndicator(
              backgroundColor: Colors.grey.shade300,
              valueColor: AlwaysStoppedAnimation<Color>(
                AppColors.primaryColor,
              ),
              minHeight: 4,
            ),
          ),
          
        const SizedBox(height: 16),
        
        // 加载文本
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: Text(
            _isLoading ? '正在加载...' : '准备就绪',
            key: ValueKey<bool>(_isLoading),
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey.shade600,
            ),
          ),
        ),
      ],
    );
  }
  
  /// 构建错误小部件
  Widget _buildErrorWidget() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // 错误图标
        Icon(
          Icons.error_outline,
          color: Colors.red.shade400,
          size: 80,
        ),
        
        const SizedBox(height: 16),
        
        // 错误消息
        Text(
          _errorMessage,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Colors.grey.shade700,
          ),
          textAlign: TextAlign.center,
        ),
        
        const SizedBox(height: 24),
        
        // 重试按钮
        ElevatedButton(
          onPressed: _retry,
          child: const Text('重试'),
        ),
      ],
    );
  }
} 