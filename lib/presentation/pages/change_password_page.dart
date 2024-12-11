import 'package:flutter/material.dart';

import '../../services/services/auth_service.dart';

class ChangePasswordPage extends StatefulWidget {
  const ChangePasswordPage({super.key});

  @override
  State<ChangePasswordPage> createState() => _ChangePasswordPageState();
}

class _ChangePasswordPageState extends State<ChangePasswordPage> {
  final _formKey = GlobalKey<FormState>();
  final _oldPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _isLoading = false;
  bool _showOldPassword = false;
  bool _showNewPassword = false;
  bool _showConfirmPassword = false;

  @override
  void dispose() {
    _oldPasswordController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _changePassword() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      // TODO: 实现修改密码逻辑
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('密码修改成功')),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('密码修改失败：$e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('修改密码'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text(
              '为了保证账号安全，请先验证当前密码',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            TextFormField(
              controller: _oldPasswordController,
              decoration: InputDecoration(
                labelText: '当前密码',
                border: const OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: Icon(
                    _showOldPassword
                        ? Icons.visibility_off
                        : Icons.visibility,
                  ),
                  onPressed: () {
                    setState(() => _showOldPassword = !_showOldPassword);
                  },
                ),
              ),
              obscureText: !_showOldPassword,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请输入当前密码';
                }
                return null;
              },
            ),
            const SizedBox(height: 24),
            TextFormField(
              controller: _newPasswordController,
              decoration: InputDecoration(
                labelText: '新密码',
                border: const OutlineInputBorder(),
                helperText: '密码长度8-20位，包含字母和数字',
                suffixIcon: IconButton(
                  icon: Icon(
                    _showNewPassword
                        ? Icons.visibility_off
                        : Icons.visibility,
                  ),
                  onPressed: () {
                    setState(() => _showNewPassword = !_showNewPassword);
                  },
                ),
              ),
              obscureText: !_showNewPassword,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请输入新密码';
                }
                if (value.length < 8 || value.length > 20) {
                  return '密码长度应为8-20位';
                }
                if (!RegExp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$')
                    .hasMatch(value)) {
                  return '密码必须包含字母和数字';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _confirmPasswordController,
              decoration: InputDecoration(
                labelText: '确认新密码',
                border: const OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: Icon(
                    _showConfirmPassword
                        ? Icons.visibility_off
                        : Icons.visibility,
                  ),
                  onPressed: () {
                    setState(() =>
                        _showConfirmPassword = !_showConfirmPassword);
                  },
                ),
              ),
              obscureText: !_showConfirmPassword,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请确认新密码';
                }
                if (value != _newPasswordController.text) {
                  return '两次输入的密码不一致';
                }
                return null;
              },
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: _isLoading ? null : _changePassword,
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('确认修改'),
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () {
                // TODO: 跳转到忘记密码页面
              },
              child: const Text('忘记当前密码？'),
            ),
          ],
        ),
      ),
    );
  }
} 