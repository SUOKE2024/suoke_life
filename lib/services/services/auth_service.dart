import 'package:flutter/foundation.dart';
import 'package:shared_preferences.dart';

class AuthService extends GetxController {
  bool _isAuthenticated = false;
  String? _token;
  Map<String, dynamic>? _userInfo;

  bool get isAuthenticated => _isAuthenticated;
  String? get token => _token;
  Map<String, dynamic>? get userInfo => _userInfo;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
    _isAuthenticated = _token != null;
    update();
  }

  Future<bool> login(String username, String password) async {
    try {
      // TODO: 实现实际的登录逻辑
      _isAuthenticated = true;
      _token = 'dummy_token';
      _userInfo = {
        'id': '1',
        'username': username,
        'role': 'user',
      };
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', _token!);
      
      update();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<void> logout() async {
    _isAuthenticated = false;
    _token = null;
    _userInfo = null;
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    
    update();
  }
} 