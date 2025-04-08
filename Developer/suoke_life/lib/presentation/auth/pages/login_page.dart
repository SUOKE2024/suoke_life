import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/presentation/auth/widgets/third_party_login_button.dart';
import 'package:suoke_life/presentation/auth/widgets/user_info_setup_card.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'dart:ui';

/// 登录状态
enum LoginStage {
  phoneLogin,
  userInfoSetup,
}

/// 登录页面
@RoutePage()
class LoginPage extends ConsumerStatefulWidget {
  final void Function()? onLoginSuccess;

  const LoginPage({super.key, this.onLoginSuccess});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage>
    with SingleTickerProviderStateMixin {
  // 登录阶段状态
  LoginStage _currentStage = LoginStage.phoneLogin;

  // 模拟手机号码 - 实际应用中应该从设备获取
  late String _phoneNumber;

  // 是否正在处理登录
  bool _isProcessing = false;

  // 动画控制器
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isPasswordVisible = false;
  String? _error;

  @override
  void initState() {
    super.initState();

    // 模拟获取本机号码
    _phoneNumber = _getDevicePhoneNumber();

    // 初始化动画
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeInOut,
      ),
    );

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  /// 模拟获取设备手机号码
  String _getDevicePhoneNumber() {
    // 实际应用中应该通过平台特定API获取
    // 这里仅作模拟
    return '138****1234';
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);
    
    // 当登录状态改变时更新UI
    ref.listen(authStateProvider, (previous, current) {
      if (current.isAuthenticated) {
        // 导航到首页
        Navigator.of(context).pushReplacementNamed('/home');
      }
      
      if (current.error != null) {
        setState(() {
          _error = current.error;
        });
      }
    });

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: Stack(
        children: [
          // 背景装饰
          _buildBackground(),

          // 主内容
          SafeArea(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              child: _currentStage == LoginStage.phoneLogin
                  ? _buildPhoneLoginView()
                  : _buildUserInfoSetupView(),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建背景装饰
  Widget _buildBackground() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Stack(
      children: [
        // 渐变背景
        Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                isDarkMode ? const Color(0xFF1A1A1A) : Colors.white,
                isDarkMode
                    ? AppColors.primaryColor.withAlpha(40)
                    : AppColors.primaryColor.withAlpha(15),
              ],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
        ),

        // 装饰圆形
        Positioned(
          right: -50,
          top: 100,
          child: Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              color: AppColors.primaryColor.withAlpha(isDarkMode ? 30 : 20),
              shape: BoxShape.circle,
            ),
          ),
        ),

        Positioned(
          left: -30,
          bottom: 200,
          child: Container(
            width: 150,
            height: 150,
            decoration: BoxDecoration(
              color: AppColors.secondaryColor.withAlpha(isDarkMode ? 30 : 20),
              shape: BoxShape.circle,
            ),
          ),
        ),
      ],
    );
  }

  /// 构建手机号码登录视图
  Widget _buildPhoneLoginView() {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 40),

            // 欢迎文字
            const Text(
              '欢迎使用索克生活',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 16),

            const Text(
              '您的健康生活管理专家',
              style: TextStyle(
                fontSize: 16,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 60),

            // 手机号码显示
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 12,
              ),
              decoration: BoxDecoration(
                color: Theme.of(context).brightness == Brightness.dark
                    ? Colors.black.withAlpha(50)
                    : Colors.white,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withAlpha(10),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  const Icon(Icons.phone_android),
                  const SizedBox(width: 16),
                  Text(
                    _phoneNumber,
                    style: const TextStyle(
                      fontSize: 18,
                    ),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () {
                      // 实际应用中应该提供修改手机号的功能
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('此功能在实际应用中将允许修改手机号'),
                        ),
                      );
                    },
                    child: const Text('更换'),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // 一键登录按钮
            _buildOneClickLoginButton(),

            const SizedBox(height: 40),

            // 第三方登录文字
            const Center(
              child: Text(
                '其他登录方式',
                style: TextStyle(
                  color: Colors.grey,
                ),
              ),
            ),

            const SizedBox(height: 20),

            // 第三方登录按钮
            _buildThirdPartyLoginButtons(),

            const Spacer(),

            // 服务协议和隐私政策
            _buildAgreementText(),
          ],
        ),
      ),
    );
  }

  /// 构建一键登录按钮
  Widget _buildOneClickLoginButton() {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: AppColors.primaryColor.withAlpha(50),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: _isProcessing ? null : _handleOneClickLogin,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primaryColor,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0,
        ),
        child: _isProcessing
            ? const SizedBox(
                height: 24,
                width: 24,
                child: CircularProgressIndicator(
                  color: Colors.white,
                  strokeWidth: 2,
                ),
              )
            : const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.login_rounded),
                  SizedBox(width: 8),
                  Text(
                    '一键登录',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  /// 构建第三方登录按钮
  Widget _buildThirdPartyLoginButtons() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        ThirdPartyLoginButton(
          icon: Icons.wechat,
          label: '微信',
          color: const Color(0xFF07C160),
          onPressed: () => _handleThirdPartyLogin('微信'),
        ),
        const SizedBox(width: 24),
        ThirdPartyLoginButton(
          icon: Icons.music_note,
          label: '抖音',
          color: const Color(0xFF000000),
          onPressed: () => _handleThirdPartyLogin('抖音'),
        ),
        const SizedBox(width: 24),
        ThirdPartyLoginButton(
          icon: Icons.redeem,
          label: '小红书',
          color: const Color(0xFFFF2442),
          onPressed: () => _handleThirdPartyLogin('小红书'),
        ),
      ],
    );
  }

  /// 构建协议文本
  Widget _buildAgreementText() {
    return Center(
      child: RichText(
        textAlign: TextAlign.center,
        text: TextSpan(
          style: TextStyle(
            fontSize: 12,
            color: Theme.of(context).brightness == Brightness.dark
                ? Colors.grey[400]
                : Colors.grey[600],
          ),
          children: [
            const TextSpan(text: '登录即表示您同意'),
            WidgetSpan(
              child: GestureDetector(
                onTap: () {
                  // TODO: 打开服务协议
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('打开服务协议')),
                  );
                },
                child: Text(
                  '《服务协议》',
                  style: TextStyle(
                    color: AppColors.primaryColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            const TextSpan(text: '和'),
            WidgetSpan(
              child: GestureDetector(
                onTap: () {
                  // TODO: 打开隐私政策
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('打开隐私政策')),
                  );
                },
                child: Text(
                  '《隐私政策》',
                  style: TextStyle(
                    color: AppColors.primaryColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建用户信息设置视图
  Widget _buildUserInfoSetupView() {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 20),

            // 提示文字
            const Text(
              '完善您的个人信息',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 8),

            const Text(
              '帮助我们为您提供更贴心的服务',
              style: TextStyle(
                fontSize: 16,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 30),

            // 用户信息设置卡片
            UserInfoSetupCard(
              onInfoCompleted: _handleUserInfoCompleted,
            ),

            const SizedBox(height: 20),

            // 服务协议和隐私政策
            _buildAgreementText(),
          ],
        ),
      ),
    );
  }

  /// 处理一键登录
  Future<void> _handleOneClickLogin() async {
    setState(() {
      _isProcessing = true;
    });

    try {
      // 模拟登录过程
      await Future.delayed(const Duration(seconds: 1));

      // 使用AuthRepository进行登录
      final authRepository = ref.read(authRepositoryProvider);
      await authRepository.loginWithPhoneNumber(_phoneNumber);

      // 切换到用户信息设置阶段
      if (mounted) {
        setState(() {
          _isProcessing = false;
          _currentStage = LoginStage.userInfoSetup;
        });
      }
    } catch (e) {
      // 处理登录错误
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });

        // 显示错误提示
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('登录失败: ${e.toString()}'),
            backgroundColor: AppColors.errorColor,
          ),
        );
      }
    }
  }

  /// 处理第三方登录
  void _handleThirdPartyLogin(String platform) {
    // 显示加载状态
    setState(() {
      _isProcessing = true;
    });

    // 显示消息
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('正在使用$platform登录...'),
      ),
    );

    // 使用AuthRepository进行第三方登录
    final authRepository = ref.read(authRepositoryProvider);
    authRepository.loginWithThirdParty(platform).then((_) {
      if (mounted) {
        setState(() {
          _isProcessing = false;
          _currentStage = LoginStage.userInfoSetup;
        });
      }
    }).catchError((error) {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });

        // 显示错误提示
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('登录失败: ${error.toString()}'),
            backgroundColor: AppColors.errorColor,
          ),
        );
      }
    });
  }

  /// 处理用户信息完成
  void _handleUserInfoCompleted() {
    // 调用登录成功回调
    if (widget.onLoginSuccess != null) {
      widget.onLoginSuccess!();
    } else {
      // 导航到主仪表盘，确保使用replaceAll方法清除导航堆栈
      context.router.replaceAll([const MainDashboardRoute()]);
    }
  }

  // 处理微信登录
  Future<void> _handleWechatLogin() async {
    try {
      final redirectUrl = 'suokelife://auth/callback';
      final authUrl = 'https://open.weixin.qq.com/connect/oauth2/authorize'
          '?appid=${Uri.encodeComponent("你的微信AppID")}'
          '&redirect_uri=${Uri.encodeComponent(redirectUrl)}'
          '&response_type=code'
          '&scope=snsapi_userinfo'
          '#wechat_redirect';

      final result = await FlutterWebAuth.authenticate(
        url: authUrl,
        callbackUrlScheme: 'suokelife',
      );

      final code = Uri.parse(result).queryParameters['code'];
      if (code != null) {
        ref.read(authStateProvider.notifier).loginWithWechat(code);
      }
    } catch (e) {
      setState(() {
        _error = '微信登录失败: $e';
      });
    }
  }

  // 处理小红书登录
  Future<void> _handleXiaohongshuLogin() async {
    try {
      final redirectUrl = 'suokelife://auth/callback';
      final authUrl = 'https://ark-api.xiaohongshu.com/authorize'
          '?client_id=${Uri.encodeComponent("你的小红书AppKey")}'
          '&redirect_uri=${Uri.encodeComponent(redirectUrl)}'
          '&response_type=code'
          '&scope=user_info';

      final result = await FlutterWebAuth.authenticate(
        url: authUrl,
        callbackUrlScheme: 'suokelife',
      );

      final code = Uri.parse(result).queryParameters['code'];
      if (code != null) {
        ref.read(authStateProvider.notifier).loginWithXiaohongshu(code, redirectUrl);
      }
    } catch (e) {
      setState(() {
        _error = '小红书登录失败: $e';
      });
    }
  }

  // 处理抖音登录
  Future<void> _handleDouyinLogin() async {
    try {
      final redirectUrl = 'suokelife://auth/callback';
      final authUrl = 'https://open.douyin.com/platform/oauth/connect'
          '?client_key=${Uri.encodeComponent("你的抖音ClientKey")}'
          '&redirect_uri=${Uri.encodeComponent(redirectUrl)}'
          '&response_type=code'
          '&scope=user_info';

      final result = await FlutterWebAuth.authenticate(
        url: authUrl,
        callbackUrlScheme: 'suokelife',
      );

      final code = Uri.parse(result).queryParameters['code'];
      if (code != null) {
        ref.read(authStateProvider.notifier).loginWithDouyin(code, redirectUrl);
      }
    } catch (e) {
      setState(() {
        _error = '抖音登录失败: $e';
      });
    }
  }
}
