import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/utils/validators.dart';
import 'package:suoke_life/core/widgets/animated_gradient_card.dart';
import 'package:suoke_life/core/widgets/animated_press_button.dart';
import 'package:suoke_life/core/widgets/form_field_wrapper.dart';
import 'package:suoke_life/presentation/auth/notifiers/auth_state_notifier.dart';
import 'package:suoke_life/di/providers/auth_providers.dart';

@RoutePage()
class RegisterPage extends ConsumerStatefulWidget {
  const RegisterPage({Key? key}) : super(key: key);

  @override
  ConsumerState<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends ConsumerState<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  
  bool _passwordVisible = false;
  bool _isLoading = false;
  bool _agreeToTerms = false;
  String? _errorMessage;

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _togglePasswordVisibility() {
    setState(() {
      _passwordVisible = !_passwordVisible;
    });
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    
    if (!_agreeToTerms) {
      setState(() {
        _errorMessage = '请阅读并同意服务协议和隐私政策';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 准备用户数据
      final userData = {
        'username': _usernameController.text,
        'email': _emailController.text,
        'password': _passwordController.text,
      };

      // 调用注册方法
      await ref.read(authStateProvider.notifier).register(userData);
      
      // 检查注册结果
      final authState = ref.read(authStateProvider);
      if (authState.isAuthenticated) {
        if (mounted) {
          // 注册成功，跳转到主页
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

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);
    
    // 如果已经在认证状态管理器中设置了loading状态，使用它
    _isLoading = authState.isLoading;
    
    // 如果有错误信息，显示它
    _errorMessage = authState.error;

    return Scaffold(
      appBar: AppBar(
        title: const Text('注册'),
        centerTitle: true,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),
              
              // Logo和应用名称
              Center(
                child: Column(
                  children: [
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
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 40),
              
              // 注册表单
              AnimatedGradientCard(
                colors: const [
                  Color(0xFFE8F7EF),
                  Color(0xFFE0F2FF),
                  Color(0xFFE8F7EF),
                ],
                borderRadius: 16,
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // 标题
                        const Text(
                          '创建新账户',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 24),
                        
                        // 错误消息
                        if (_errorMessage != null)
                          Container(
                            padding: const EdgeInsets.all(10),
                            margin: const EdgeInsets.only(bottom: 16),
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
                            ),
                          ),
                        
                        // 用户名输入框
                        FormFieldWrapper(
                          label: '用户名',
                          child: TextFormField(
                            controller: _usernameController,
                            decoration: const InputDecoration(
                              hintText: '请输入用户名',
                              prefixIcon: Icon(Icons.person_outline),
                            ),
                            validator: Validators.validateUsername,
                          ),
                        ),
                        const SizedBox(height: 16),
                        
                        // 邮箱输入框
                        FormFieldWrapper(
                          label: '邮箱',
                          child: TextFormField(
                            controller: _emailController,
                            decoration: const InputDecoration(
                              hintText: '请输入邮箱',
                              prefixIcon: Icon(Icons.email_outlined),
                            ),
                            keyboardType: TextInputType.emailAddress,
                            validator: Validators.validateEmail,
                          ),
                        ),
                        const SizedBox(height: 16),
                        
                        // 密码输入框
                        FormFieldWrapper(
                          label: '密码',
                          child: TextFormField(
                            controller: _passwordController,
                            decoration: InputDecoration(
                              hintText: '请输入密码',
                              prefixIcon: const Icon(Icons.lock_outline),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _passwordVisible 
                                    ? Icons.visibility_outlined 
                                    : Icons.visibility_off_outlined,
                                ),
                                onPressed: _togglePasswordVisibility,
                              ),
                            ),
                            obscureText: !_passwordVisible,
                            validator: Validators.validatePassword,
                          ),
                        ),
                        const SizedBox(height: 16),
                        
                        // 确认密码输入框
                        FormFieldWrapper(
                          label: '确认密码',
                          child: TextFormField(
                            controller: _confirmPasswordController,
                            decoration: InputDecoration(
                              hintText: '请再次输入密码',
                              prefixIcon: const Icon(Icons.lock_outline),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _passwordVisible 
                                    ? Icons.visibility_outlined 
                                    : Icons.visibility_off_outlined,
                                ),
                                onPressed: _togglePasswordVisibility,
                              ),
                            ),
                            obscureText: !_passwordVisible,
                            validator: (value) => Validators.validateConfirmPassword(
                              value, 
                              _passwordController.text,
                            ),
                          ),
                        ),
                        const SizedBox(height: 24),
                        
                        // 同意条款复选框
                        Row(
                          children: [
                            SizedBox(
                              width: 24,
                              height: 24,
                              child: Checkbox(
                                value: _agreeToTerms,
                                onChanged: (value) {
                                  setState(() {
                                    _agreeToTerms = value ?? false;
                                    if (_agreeToTerms) {
                                      _errorMessage = null;
                                    }
                                  });
                                },
                                activeColor: AppColors.primaryColor,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text.rich(
                                TextSpan(
                                  text: '我已阅读并同意',
                                  style: const TextStyle(fontSize: 14),
                                  children: [
                                    TextSpan(
                                      text: '《服务协议》',
                                      style: TextStyle(
                                        color: AppColors.primaryColor,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                    const TextSpan(text: '和'),
                                    TextSpan(
                                      text: '《隐私政策》',
                                      style: TextStyle(
                                        color: AppColors.primaryColor,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                        
                        // 注册按钮
                        AnimatedPressButton(
                          onPressed: _isLoading ? null : _register,
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
                                  '注册',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              
              const SizedBox(height: 20),
              
              // 已有账户提示
              Center(
                child: TextButton(
                  onPressed: () {
                    context.router.replace(const LoginRoute());
                  },
                  child: Text.rich(
                    TextSpan(
                      text: '已有账户？',
                      style: const TextStyle(color: Colors.black87),
                      children: [
                        TextSpan(
                          text: '立即登录',
                          style: TextStyle(
                            color: AppColors.primaryColor,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 