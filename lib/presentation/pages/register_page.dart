import 'package:flutter/material.dart';
import '../../core/auth/models/auth_models.dart';
import '../../core/auth/services/auth_service.dart';
import '../widgets/phone_input.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _phoneController = TextEditingController();
  final _codeController = TextEditingController();
  final _nicknameController = TextEditingController();
  final _inviteCodeController = TextEditingController();
  final _authService = AuthService.instance;
  bool _isLoading = false;
  bool _isPhoneVerified = false;

  @override
  void dispose() {
    _phoneController.dispose();
    _codeController.dispose();
    _nicknameController.dispose();
    _inviteCodeController.dispose();
    super.dispose();
  }

  Future<void> _sendVerificationCode() async {
    final phone = _phoneController.text;
    if (phone.length != 11) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入正确的手机号')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      await _authService.sendVerificationCode(phone);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('验证码已发送')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送验证码失败: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _verifyPhone() async {
    final phone = _phoneController.text;
    final code = _codeController.text;

    if (phone.length != 11) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入正确的手机号')),
      );
      return;
    }

    if (code.length != 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入6位验证码')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      await _authService.verifyPhone(PhoneAuthRequest(
        phone: phone,
        verificationCode: code,
      ));
      
      setState(() => _isPhoneVerified = true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('验证失败: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _completeRegistration() async {
    final nickname = _nicknameController.text;
    if (nickname.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入昵称')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final profile = UserProfile(
        id: '',  // 将由服务器生成
        phone: _phoneController.text,
        nickname: nickname,
        createdAt: DateTime.now(),
      );
      
      await _authService.updateProfile(profile);
      
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('注册失败: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('注册'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (!_isPhoneVerified) ...[
              PhoneInput(
                controller: _phoneController,
                onSendCode: _isLoading ? null : _sendVerificationCode,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _codeController,
                decoration: const InputDecoration(
                  labelText: '验证码',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                maxLength: 6,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _verifyPhone,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                        ),
                      )
                    : const Text('验证手机号'),
              ),
            ] else ...[
              TextField(
                controller: _nicknameController,
                decoration: const InputDecoration(
                  labelText: '昵称',
                  border: OutlineInputBorder(),
                ),
                maxLength: 20,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _inviteCodeController,
                decoration: const InputDecoration(
                  labelText: '邀请码(选填)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _completeRegistration,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                        ),
                      )
                    : const Text('完成注册'),
              ),
            ],
            const SizedBox(height: 16),
            if (!_isPhoneVerified)
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('已有账号？'),
                  TextButton(
                    onPressed: () {
                      Navigator.pushReplacementNamed(context, '/login');
                    },
                    child: const Text('立即登录'),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
} 