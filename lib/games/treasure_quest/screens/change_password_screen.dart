import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class ChangePasswordScreen extends StatefulWidget {
  const ChangePasswordScreen({Key? key}) : super(key: key);

  @override
  State<ChangePasswordScreen> createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _authService = AuthService();
  bool _isLoading = false;
  bool _obscureCurrentPassword = true;
  bool _obscureNewPassword = true;
  bool _obscureConfirmPassword = true;

  final _currentPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  @override
  void dispose() {
    _currentPasswordController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _changePassword() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final success = await _authService.changePassword(
      currentPassword: _currentPasswordController.text,
      newPassword: _newPasswordController.text,
      confirmPassword: _confirmPasswordController.text,
    );

    setState(() => _isLoading = false);

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('密码修改成功'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.of(context).pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('密码修改失败，请检查当前密码是否正确'),
          backgroundColor: Colors.red,
        ),
      );
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
            // 当前密码
            TextFormField(
              controller: _currentPasswordController,
              decoration: InputDecoration(
                labelText: '当前密码',
                prefixIcon: const Icon(Icons.lock_outline),
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscureCurrentPassword
                        ? Icons.visibility_off
                        : Icons.visibility,
                  ),
                  onPressed: () {
                    setState(() {
                      _obscureCurrentPassword = !_obscureCurrentPassword;
                    });
                  },
                ),
              ),
              obscureText: _obscureCurrentPassword,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请输入当前密码';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),

            // 新密码
            TextFormField(
              controller: _newPasswordController,
              decoration: InputDecoration(
                labelText: '新密码',
                prefixIcon: const Icon(Icons.lock),
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscureNewPassword
                        ? Icons.visibility_off
                        : Icons.visibility,
                  ),
                  onPressed: () {
                    setState(() {
                      _obscureNewPassword = !_obscureNewPassword;
                    });
                  },
                ),
              ),
              obscureText: _obscureNewPassword,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请输入新密码';
                }
                if (value.length < 8) {
                  return '密码长度至少为8位';
                }
                if (!value.contains(RegExp(r'[A-Z]'))) {
                  return '密码必须包含大写字母';
                }
                if (!value.contains(RegExp(r'[a-z]'))) {
                  return '密码必须包含小写字母';
                }
                if (!value.contains(RegExp(r'[0-9]'))) {
                  return '密码必须包含数字';
                }
                if (!value.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) {
                  return '密码必须包含特殊字符';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),

            // 确认新密码
            TextFormField(
              controller: _confirmPasswordController,
              decoration: InputDecoration(
                labelText: '确认新密码',
                prefixIcon: const Icon(Icons.lock),
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscureConfirmPassword
                        ? Icons.visibility_off
                        : Icons.visibility,
                  ),
                  onPressed: () {
                    setState(() {
                      _obscureConfirmPassword = !_obscureConfirmPassword;
                    });
                  },
                ),
              ),
              obscureText: _obscureConfirmPassword,
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
            const SizedBox(height: 24),

            // 密码要求提示
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '密码要求：',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  _buildPasswordRequirement('至少8个字符'),
                  _buildPasswordRequirement('至少包含一个大写字母'),
                  _buildPasswordRequirement('至少包含一个小写字母'),
                  _buildPasswordRequirement('至少包含一个数字'),
                  _buildPasswordRequirement('至少包含一个特殊字符 (!@#\$%^&*(),.?":{}|<>)'),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 提交按钮
            ElevatedButton(
              onPressed: _isLoading ? null : _changePassword,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                      ),
                    )
                  : const Text('修改密码'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPasswordRequirement(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          const Icon(
            Icons.check_circle_outline,
            size: 16,
            color: Colors.grey,
          ),
          const SizedBox(width: 8),
          Text(
            text,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }
} 