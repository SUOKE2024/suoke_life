import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/router/app_router.dart';
import '../../../presentation/providers/auth_providers.dart';
import '../../widgets/form/form_field_wrapper.dart';

@RoutePage()
class LoginScreen extends ConsumerStatefulWidget {
  final String? returnUrl;

  const LoginScreen({Key? key, this.returnUrl}) : super(key: key);

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _errorMessage;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    // 隐藏键盘
    FocusScope.of(context).unfocus();

    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final success = await ref.read(authStateProvider.notifier).login(
            _usernameController.text,
            _passwordController.text,
          );

      if (success) {
        if (context.mounted) {
          // 导航到目标页面或主页
          if (widget.returnUrl != null) {
            context.router.navigateNamed(widget.returnUrl!);
          } else {
            context.router.replace(const HomeRoute());
          }
        }
      } else {
        setState(() {
          _errorMessage = '登录失败，请检查用户名和密码';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = '登录时发生错误: ${e.toString()}';
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
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('登录'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // 应用logo
                  const Padding(
                    padding: EdgeInsets.only(bottom: 32),
                    child: Icon(
                      Icons.health_and_safety,
                      size: 80,
                      color: Colors.green,
                    ),
                  ),
                  
                  // 标题
                  Text(
                    '欢迎回到索克生活',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '请登录您的账号以继续',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.textTheme.bodySmall?.color,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),
                  
                  // 错误信息
                  if (_errorMessage != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.red.shade200),
                        ),
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(color: Colors.red.shade800),
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
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入用户名';
                        }
                        return null;
                      },
                      textInputAction: TextInputAction.next,
                      enabled: !_isLoading,
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
                            _obscurePassword
                                ? Icons.visibility_off
                                : Icons.visibility,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscurePassword = !_obscurePassword;
                            });
                          },
                        ),
                      ),
                      obscureText: _obscurePassword,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入密码';
                        }
                        return null;
                      },
                      textInputAction: TextInputAction.done,
                      onFieldSubmitted: (_) => _login(),
                      enabled: !_isLoading,
                    ),
                  ),
                  
                  // 忘记密码
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton(
                      onPressed: _isLoading
                          ? null
                          : () {
                              // 导航到忘记密码页面
                              context.router.push(const ForgotPasswordRoute());
                            },
                      child: const Text('忘记密码?'),
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // 登录按钮
                  SizedBox(
                    height: 54,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _login,
                      style: ElevatedButton.styleFrom(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              height: 24,
                              width: 24,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Text('登录'),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // 注册账号
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '还没有账号?',
                        style: TextStyle(
                          color: theme.textTheme.bodySmall?.color,
                        ),
                      ),
                      TextButton(
                        onPressed: _isLoading
                            ? null
                            : () {
                                // 导航到注册页面
                                context.router.push(const RegisterRoute());
                              },
                        child: const Text('立即注册'),
                      ),
                    ],
                  ),
                  
                  // 访客模式
                  TextButton(
                    onPressed: _isLoading
                        ? null
                        : () {
                            // 以访客身份继续
                            context.router.replace(const HomeRoute());
                          },
                    child: const Text('以访客身份继续'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
} 