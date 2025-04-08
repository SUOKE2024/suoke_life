import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/widgets/animated_gradient_card.dart';
import 'package:suoke_life/core/widgets/animated_press_button.dart';
import 'package:suoke_life/di/providers/auth_providers.dart';

@RoutePage()
class TwoFactorAuthPage extends ConsumerStatefulWidget {
  const TwoFactorAuthPage({Key? key, this.temporaryToken}) : super(key: key);
  
  final String? temporaryToken;

  @override
  ConsumerState<TwoFactorAuthPage> createState() => _TwoFactorAuthPageState();
}

class _TwoFactorAuthPageState extends ConsumerState<TwoFactorAuthPage> {
  final List<TextEditingController> _controllers = List.generate(
    6,
    (index) => TextEditingController(),
  );
  final List<FocusNode> _focusNodes = List.generate(
    6,
    (index) => FocusNode(),
  );
  
  bool _isLoading = false;
  String? _errorMessage;
  
  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    for (var node in _focusNodes) {
      node.dispose();
    }
    super.dispose();
  }

  void _handleVerify() async {
    // 收集验证码
    final code = _controllers.map((c) => c.text).join();
    
    if (code.length != 6) {
      setState(() {
        _errorMessage = '请输入完整的6位验证码';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 调用验证方法
      await ref.read(authStateProvider.notifier).verify2FA(
        widget.temporaryToken ?? '',
        code,
      );
      
      // 检查验证结果
      final authState = ref.read(authStateProvider);
      if (authState.isAuthenticated) {
        if (mounted) {
          // 验证成功，跳转到主页
          context.router.replace(const MainDashboardRoute());
        }
      } else if (authState.error != null) {
        setState(() {
          _errorMessage = authState.error;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  // 处理使用备份码
  void _handleUseBackupCode() {
    // 这里可以导航到备份码页面
    // 暂时仅显示提示
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('备份码功能即将上线'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);
    
    // 如果已经在认证状态管理器中设置了loading状态，使用它
    _isLoading = authState.isLoading;
    
    // 如果有错误信息，显示它
    if (authState.error != null) {
      _errorMessage = authState.error;
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('双因素认证'),
        centerTitle: true,
        elevation: 0,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Logo和应用名称
              Image.asset(
                'assets/images/logo.png',
                width: 80,
                height: 80,
              ),
              const SizedBox(height: 12),
              const Text(
                '索克生活',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                '您的健康生活管理专家',
                style: TextStyle(
                  fontSize: 16,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 40),
              
              // 验证码卡片
              AnimatedGradientCard(
                colors: const [
                  Color(0xFFE8F7EF),
                  Color(0xFFE0F2FF),
                  Color(0xFFE8F7EF),
                ],
                borderRadius: 16,
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // 安全图标
                      Icon(
                        Icons.security,
                        size: 60,
                        color: AppColors.primaryColor,
                      ),
                      
                      const SizedBox(height: 20),
                      
                      // 标题
                      const Text(
                        '双重安全验证',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      
                      const SizedBox(height: 12),
                      
                      // 提示文字
                      const Text(
                        '请输入您的认证应用生成的6位验证码',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.black54,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // 错误信息
                      if (_errorMessage != null)
                        Container(
                          padding: const EdgeInsets.all(10),
                          margin: const EdgeInsets.only(bottom: 16),
                          width: double.infinity,
                          decoration: BoxDecoration(
                            color: AppColors.errorColor.withAlpha(30),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            _errorMessage!,
                            style: TextStyle(
                              color: AppColors.errorColor,
                              fontSize: 14,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      
                      // 验证码输入框
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: List.generate(
                          6,
                          (index) => SizedBox(
                            width: 40,
                            child: TextField(
                              controller: _controllers[index],
                              focusNode: _focusNodes[index],
                              keyboardType: TextInputType.number,
                              textAlign: TextAlign.center,
                              maxLength: 1,
                              decoration: InputDecoration(
                                counterText: '',
                                contentPadding: const EdgeInsets.symmetric(vertical: 12),
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(8),
                                  borderSide: BorderSide(color: AppColors.lightBorder),
                                ),
                                focusedBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(8),
                                  borderSide: BorderSide(color: AppColors.primaryColor, width: 2),
                                ),
                                filled: true,
                                fillColor: Colors.white,
                              ),
                              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                              onChanged: (value) {
                                if (value.isNotEmpty && index < 5) {
                                  _focusNodes[index + 1].requestFocus();
                                }
                              },
                            ),
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // 验证按钮
                      AnimatedPressButton(
                        onPressed: _isLoading ? null : _handleVerify,
                        child: _isLoading
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Text(
                                '验证',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      // 使用备份码
                      TextButton(
                        onPressed: _handleUseBackupCode,
                        child: Text(
                          '使用备份码',
                          style: TextStyle(
                            color: AppColors.primaryColor,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 20),
              
              // 帮助提示
              Text.rich(
                TextSpan(
                  text: '需要帮助？',
                  style: const TextStyle(color: Colors.black54, fontSize: 14),
                  children: [
                    TextSpan(
                      text: ' 联系客服',
                      style: TextStyle(
                        color: AppColors.primaryColor,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}