import 'package:get/get.dart';
import '../models/auth_models.dart';
import '../../network/dio_client.dart';
import '../../storage/services/secure_storage_service.dart';
import 'login_log_service.dart';
import 'security_policy_service.dart';

class AuthService extends GetxService {
  static AuthService get to => Get.find();
  
  final _dioClient = Get.find<DioClient>();
  final _storage = Get.find<SecureStorageService>();
  final _loginLogService = Get.find<LoginLogService>();
  final _securityPolicy = Get.find<SecurityPolicyService>();
  
  final _isLoggedIn = false.obs;
  final _isAutoLoginEnabled = false.obs;
  final _lastLoginType = ''.obs;
  final _userId = ''.obs;
  
  bool get isLoggedIn => _isLoggedIn.value;
  bool get isAutoLoginEnabled => _isAutoLoginEnabled.value;
  String get lastLoginType => _lastLoginType.value;
  String get userId => _userId.value;
  
  // 初始化服务
  Future<AuthService> init() async {
    // 检查是否启用了自动登录
    final autoLogin = await _storage.read('auto_login_enabled');
    _isAutoLoginEnabled.value = autoLogin == 'true';
    
    // 获取上次登录方式
    final lastType = await _storage.read('last_login_type');
    if (lastType != null) {
      _lastLoginType.value = lastType;
    }
    
    // 获取用户ID
    final id = await _storage.read('user_id');
    if (id != null) {
      _userId.value = id;
    }
    
    // 如果启用了自动登录，尝试自动登录
    if (_isAutoLoginEnabled.value) {
      await _tryAutoLogin();
    } else {
      // 检查是否有存储的token
      final token = await _storage.read('auth_token');
      if (token != null) {
        _isLoggedIn.value = true;
        _dioClient.setAuthToken(token);
      }
    }
    
    return this;
  }
  
  // 尝试自动登录
  Future<bool> _tryAutoLogin() async {
    try {
      final token = await _storage.read('auth_token');
      if (token == null) return false;
      
      // 验证token是否有效
      final isValid = await checkLoginStatus();
      if (!isValid) {
        // token无效，尝试刷新
        final refreshSuccess = await refreshToken();
        if (!refreshSuccess) {
          // 刷新失败，清理登录状态
          await logout();
          return false;
        }
      }
      
      _isLoggedIn.value = true;
      _dioClient.setAuthToken(token);
      
      // 记录自动登录日志
      await _loginLogService.recordLogin(
        userId: _userId.value,
        loginType: 'auto',
        isSuccess: true,
      );
      
      return true;
    } catch (e) {
      // 记录失败日志
      await _loginLogService.recordLogin(
        userId: _userId.value,
        loginType: 'auto',
        isSuccess: false,
        failureReason: e.toString(),
      );
      return false;
    }
  }
  
  // 发送验证码
  Future<bool> sendVerificationCode(String phone) async {
    // 检查是否被锁定
    if (_securityPolicy.isLocked) {
      final duration = _securityPolicy.policy.lockoutDuration;
      throw Exception('账号已被锁定，请 $duration 分钟后重试');
    }
    
    // 检查验证码冷却时间
    if (await _securityPolicy.isCodeInCooldown()) {
      final cooldown = _securityPolicy.policy.codeCooldownSeconds;
      throw Exception('请等待 $cooldown 秒后再次发送验证码');
    }
    
    // 检查每日验证码次数限制
    if (!await _securityPolicy.canRequestCode()) {
      final maxRequests = _securityPolicy.policy.maxDailyCodeRequests;
      throw Exception('今日验证码发送次数已达上限 $maxRequests 次');
    }
    
    try {
      final response = await _dioClient.post(
        '/auth/send-code',
        data: {'phone': phone},
      );
      
      if (response.data['success'] == true) {
        await _securityPolicy.recordCodeSend();
      }
      
      return response.data['success'] ?? false;
    } catch (e) {
      rethrow;
    }
  }
  
  // 手机号登录
  Future<bool> login({
    required String phone,
    required String code,
  }) async {
    // 检查是否被锁定
    if (_securityPolicy.isLocked) {
      final duration = _securityPolicy.policy.lockoutDuration;
      throw Exception('账号已被锁定，请 $duration 分钟后重试');
    }
    
    // 检查验证码长度
    if (code.length != _securityPolicy.policy.codeLength) {
      throw Exception('验证码长度不正确');
    }
    
    try {
      final response = await _dioClient.post(
        '/auth/login',
        data: {
          'phone': phone,
          'code': code,
        },
      );
      
      if (response.data['token'] != null) {
        await _handleLoginSuccess(
          token: response.data['token'],
          loginType: 'phone',
          userId: response.data['user_id'],
        );
        
        // 记录登录日志
        await _loginLogService.recordLogin(
          userId: _userId.value,
          loginType: 'phone',
          isSuccess: true,
        );
        
        // 重置登录失败计数
        await _securityPolicy.onLoginSuccess();
        
        return true;
      }
      
      // 记录登录失败
      await _securityPolicy.recordLoginFail();
      
      // 记录失败日志
      await _loginLogService.recordLogin(
        userId: phone,
        loginType: 'phone',
        isSuccess: false,
        failureReason: '验证码错误',
      );
      
      return false;
    } catch (e) {
      // 记录登录失败
      await _securityPolicy.recordLoginFail();
      
      // 记录失败日志
      await _loginLogService.recordLogin(
        userId: phone,
        loginType: 'phone',
        isSuccess: false,
        failureReason: e.toString(),
      );
      
      rethrow;
    }
  }
  
  // 微信登录
  Future<bool> loginWithWeChatCode({required String code}) async {
    try {
      final response = await _dioClient.post(
        '/auth/wechat/login',
        data: {'code': code},
      );
      
      if (response.data['token'] != null) {
        await _handleLoginSuccess(
          token: response.data['token'],
          loginType: 'wechat',
          userId: response.data['user_id'],
        );
        
        // 记录登录日志
        await _loginLogService.recordLogin(
          userId: _userId.value,
          loginType: 'wechat',
          isSuccess: true,
        );
        
        return true;
      }
      
      // 记录失败日志
      await _loginLogService.recordLogin(
        userId: 'unknown',
        loginType: 'wechat',
        isSuccess: false,
        failureReason: '微信授权失败',
      );
      
      return false;
    } catch (e) {
      // 记录失败日志
      await _loginLogService.recordLogin(
        userId: 'unknown',
        loginType: 'wechat',
        isSuccess: false,
        failureReason: e.toString(),
      );
      rethrow;
    }
  }
  
  // 支付宝登录
  Future<bool> loginWithAlipayCode({required String code}) async {
    try {
      final response = await _dioClient.post(
        '/auth/alipay/login',
        data: {'auth_code': code},
      );
      
      if (response.data['token'] != null) {
        await _handleLoginSuccess(
          token: response.data['token'],
          loginType: 'alipay',
          userId: response.data['user_id'],
        );
        
        // 记录登录日志
        await _loginLogService.recordLogin(
          userId: _userId.value,
          loginType: 'alipay',
          isSuccess: true,
        );
        
        return true;
      }
      
      // 记录失败日志
      await _loginLogService.recordLogin(
        userId: 'unknown',
        loginType: 'alipay',
        isSuccess: false,
        failureReason: '支付宝授权失败',
      );
      
      return false;
    } catch (e) {
      // 记录失败日志
      await _loginLogService.recordLogin(
        userId: 'unknown',
        loginType: 'alipay',
        isSuccess: false,
        failureReason: e.toString(),
      );
      rethrow;
    }
  }
  
  // 生物识别登录
  Future<bool> loginWithBiometric() async {
    if (!_securityPolicy.canUseBiometric()) {
      throw Exception('生物识别登录未启用');
    }
    
    // 继续生物识别登录流程...
    return false;
  }
  
  // 声纹登录
  Future<bool> loginWithVoicePrint() async {
    if (!_securityPolicy.canUseVoicePrint()) {
      throw Exception('声纹登录未启用');
    }
    
    // 继续声纹登录流程...
    return false;
  }
  
  // 处理登录成功
  Future<void> _handleLoginSuccess({
    required String token,
    required String loginType,
    required String userId,
  }) async {
    await _storage.write('auth_token', token);
    await _storage.write('last_login_type', loginType);
    await _storage.write('user_id', userId);
    _lastLoginType.value = loginType;
    _userId.value = userId;
    _dioClient.setAuthToken(token);
    _isLoggedIn.value = true;
  }
  
  // 启用自动登录
  Future<void> enableAutoLogin() async {
    await _storage.write('auto_login_enabled', 'true');
    _isAutoLoginEnabled.value = true;
  }
  
  // 禁用自动登录
  Future<void> disableAutoLogin() async {
    await _storage.write('auto_login_enabled', 'false');
    _isAutoLoginEnabled.value = false;
  }
  
  // 登出
  Future<void> logout() async {
    try {
      await _dioClient.post('/auth/logout');
      
      // 记录登出日志
      await _loginLogService.recordLogin(
        userId: _userId.value,
        loginType: 'logout',
        isSuccess: true,
      );
    } catch (e) {
      // 即使请求失败也继续清理本地数据
      await _loginLogService.recordLogin(
        userId: _userId.value,
        loginType: 'logout',
        isSuccess: false,
        failureReason: e.toString(),
      );
    } finally {
      await _storage.delete('auth_token');
      await _storage.delete('last_login_type');
      await _storage.delete('user_id');
      _dioClient.clearAuthToken();
      _isLoggedIn.value = false;
      _lastLoginType.value = '';
      _userId.value = '';
    }
  }
  
  // 检查登录状态
  Future<bool> checkLoginStatus() async {
    try {
      final response = await _dioClient.get('/auth/status');
      return response.data['isValid'] ?? false;
    } catch (e) {
      return false;
    }
  }
  
  // 刷新Token
  Future<bool> refreshToken() async {
    try {
      final response = await _dioClient.post('/auth/refresh-token');
      
      if (response.data['token'] != null) {
        await _handleLoginSuccess(
          token: response.data['token'],
          loginType: _lastLoginType.value,
          userId: _userId.value,
        );
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
} 