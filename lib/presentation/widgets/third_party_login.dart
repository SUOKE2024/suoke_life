import 'package:flutter/material.dart';
import '../../core/auth/services/third_party_auth_service.dart';
import '../../core/auth/services/auth_service.dart';

class ThirdPartyLogin extends StatefulWidget {
  const ThirdPartyLogin({super.key});

  @override
  State<ThirdPartyLogin> createState() => _ThirdPartyLoginState();
}

class _ThirdPartyLoginState extends State<ThirdPartyLogin> {
  final _thirdPartyAuthService = ThirdPartyAuthService.instance;
  final _authService = AuthService.instance;
  bool _isLoading = false;
  bool _isWechatAvailable = false;
  bool _isAlipayAvailable = false;

  @override
  void initState() {
    super.initState();
    _checkAvailability();
  }

  Future<void> _checkAvailability() async {
    final wechatInstalled = await _thirdPartyAuthService.isWechatInstalled();
    final alipayInstalled = await _thirdPartyAuthService.isAlipayInstalled();

    setState(() {
      _isWechatAvailable = wechatInstalled;
      _isAlipayAvailable = alipayInstalled;
    });
  }

  Future<void> _handleWechatLogin() async {
    if (!_isWechatAvailable) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请先安装微信')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final response = await _thirdPartyAuthService.loginWithWechat();
      await _authService.handleAuthResponse(response);
      
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('微信登录失败: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _handleAlipayLogin() async {
    if (!_isAlipayAvailable) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请先安装支付宝')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final response = await _thirdPartyAuthService.loginWithAlipay();
      await _authService.handleAuthResponse(response);
      
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('支付宝登录失败: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isWechatAvailable && !_isAlipayAvailable) {
      return const SizedBox.shrink();
    }

    return Column(
      children: [
        const Row(
          children: [
            Expanded(child: Divider()),
            Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Text('其他登录方式'),
            ),
            Expanded(child: Divider()),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            if (_isWechatAvailable)
              _buildLoginButton(
                icon: 'assets/images/wechat.png',
                label: '微信登录',
                onPressed: _isLoading ? null : _handleWechatLogin,
              ),
            if (_isAlipayAvailable)
              _buildLoginButton(
                icon: 'assets/images/alipay.png',
                label: '支付宝登录',
                onPressed: _isLoading ? null : _handleAlipayLogin,
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildLoginButton({
    required String icon,
    required String label,
    VoidCallback? onPressed,
  }) {
    return Column(
      children: [
        IconButton(
          icon: Image.asset(
            icon,
            width: 32,
            height: 32,
          ),
          onPressed: onPressed,
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
        ),
      ],
    );
  }
} 