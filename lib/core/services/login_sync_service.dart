import 'package:get/get.dart';
import '../core/network/api_client.dart';
import '../services/auth_service.dart';
import '../services/device_manager_service.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

class LoginSyncService extends GetxService {
  final ApiClient _apiClient;
  final AuthService _authService;
  final DeviceManagerService _deviceManager;

  LoginSyncService({
    required ApiClient apiClient,
    required AuthService authService,
    required DeviceManagerService deviceManager,
  })  : _apiClient = apiClient,
        _authService = authService,
        _deviceManager = deviceManager;

  WebSocketChannel? _channel;
  bool _isConnected = false;

  @override
  void onInit() {
    super.onInit();
    _setupAuthListener();
  }

  void _setupAuthListener() {
    ever(_authService.isAuthenticated, (bool isAuthenticated) {
      if (isAuthenticated) {
        _connect();
      } else {
        _disconnect();
      }
    });
  }

  Future<void> _connect() async {
    if (_isConnected) return;

    try {
      // 获取WebSocket连接URL和token
      final response = await _apiClient.get('/auth/ws-token');
      final wsUrl = response['ws_url'];
      final wsToken = response['token'];

      // 建立WebSocket连接
      _channel = WebSocketChannel.connect(
        Uri.parse('$wsUrl?token=$wsToken'),
      );

      // 监听消息
      _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDone,
      );

      _isConnected = true;
    } catch (e) {
      debugPrint('WebSocket连接失败: $e');
    }
  }

  void _disconnect() {
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
  }

  void _handleMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String);
      switch (data['type']) {
        case 'logout':
          _handleLogout(data);
          break;
        case 'device_revoked':
          _handleDeviceRevoked(data);
          break;
        case 'password_changed':
          _handlePasswordChanged(data);
          break;
      }
    } catch (e) {
      debugPrint('处理WebSocket消息失败: $e');
    }
  }

  void _handleLogout(Map<String, dynamic> data) {
    if (data['device_id'] == _deviceManager.currentDeviceId.value) {
      _authService.logout();
      Get.snackbar('提示', '您的账号已在其他设备登出');
    }
  }

  void _handleDeviceRevoked(Map<String, dynamic> data) {
    if (data['device_id'] == _deviceManager.currentDeviceId.value) {
      _authService.logout();
      Get.snackbar('提示', '您的设备已被移除登录授权');
    }
  }

  void _handlePasswordChanged(Map<String, dynamic> data) {
    _authService.logout();
    Get.snackbar('提示', '您的密码已被修改，请重新登录');
  }

  void _handleError(error) {
    debugPrint('WebSocket错误: $error');
    _reconnect();
  }

  void _handleDone() {
    debugPrint('WebSocket连接已关闭');
    _reconnect();
  }

  void _reconnect() {
    if (!_authService.isAuthenticated.value) return;

    Future.delayed(const Duration(seconds: 5), () {
      if (!_isConnected && _authService.isAuthenticated.value) {
        _connect();
      }
    });
  }

  @override
  void onClose() {
    _disconnect();
    super.onClose();
  }
} 