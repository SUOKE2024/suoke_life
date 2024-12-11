import 'package:get/get.dart';
import '../models/security_policy.dart';
import '../../network/dio_client.dart';
import '../../storage/services/secure_storage_service.dart';

class SecurityPolicyService extends GetxService {
  static SecurityPolicyService get to => Get.find();
  
  final _dioClient = Get.find<DioClient>();
  final _storage = Get.find<SecureStorageService>();
  
  final _policy = Rx<SecurityPolicy>(SecurityPolicy());
  SecurityPolicy get policy => _policy.value;
  
  // 登录失败计数
  final _loginFailCount = 0.obs;
  final _lastFailTime = Rx<DateTime?>(null);
  final _isLocked = false.obs;
  
  int get loginFailCount => _loginFailCount.value;
  DateTime? get lastFailTime => _lastFailTime.value;
  bool get isLocked => _isLocked.value;
  
  // 初始化服务
  Future<SecurityPolicyService> init() async {
    await _loadPolicy();
    await _loadLoginState();
    return this;
  }
  
  // 加载安全策略
  Future<void> _loadPolicy() async {
    try {
      final response = await _dioClient.get('/auth/security/policy');
      _policy.value = SecurityPolicy.fromJson(response.data);
    } catch (e) {
      // 加载失败时使用默认策略
      _policy.value = SecurityPolicy();
    }
  }
  
  // 加载登录状态
  Future<void> _loadLoginState() async {
    final count = await _storage.read('login_fail_count');
    final time = await _storage.read('last_fail_time');
    
    if (count != null) {
      _loginFailCount.value = int.parse(count);
    }
    
    if (time != null) {
      _lastFailTime.value = DateTime.parse(time);
      _checkLockStatus();
    }
  }
  
  // 检查锁定状态
  void _checkLockStatus() {
    if (_lastFailTime.value == null) {
      _isLocked.value = false;
      return;
    }
    
    final lockoutEnd = _lastFailTime.value!.add(
      Duration(minutes: policy.lockoutDuration),
    );
    
    if (DateTime.now().isBefore(lockoutEnd) &&
        _loginFailCount.value >= policy.maxLoginAttempts) {
      _isLocked.value = true;
    } else {
      _isLocked.value = false;
      if (_loginFailCount.value >= policy.maxLoginAttempts) {
        _resetFailCount();
      }
    }
  }
  
  // 记录登录失败
  Future<void> recordLoginFail() async {
    _loginFailCount.value++;
    _lastFailTime.value = DateTime.now();
    
    await _storage.write(
      'login_fail_count',
      _loginFailCount.value.toString(),
    );
    await _storage.write(
      'last_fail_time',
      _lastFailTime.value!.toIso8601String(),
    );
    
    _checkLockStatus();
  }
  
  // 重置失败计数
  Future<void> _resetFailCount() async {
    _loginFailCount.value = 0;
    _lastFailTime.value = null;
    _isLocked.value = false;
    
    await _storage.delete('login_fail_count');
    await _storage.delete('last_fail_time');
  }
  
  // 登录成功处理
  Future<void> onLoginSuccess() async {
    await _resetFailCount();
  }
  
  // 检查是否需要验证码
  bool needCaptcha() {
    return policy.requireCaptcha &&
           _loginFailCount.value >= policy.captchaThreshold;
  }
  
  // 检查设备是否可信
  Future<bool> isDeviceTrusted(String deviceId) async {
    if (!policy.trustedDevicesOnly) return true;
    
    try {
      final response = await _dioClient.get(
        '/auth/security/device/trust',
        queryParameters: {'deviceId': deviceId},
      );
      return response.data['trusted'] ?? false;
    } catch (e) {
      return false;
    }
  }
  
  // 信任设备
  Future<void> trustDevice(String deviceId) async {
    try {
      await _dioClient.post(
        '/auth/security/device/trust',
        data: {'deviceId': deviceId},
      );
    } catch (e) {
      rethrow;
    }
  }
  
  // 检查位置是否允许
  Future<bool> isLocationAllowed(String country, String ip) async {
    if (!policy.locationCheck) return true;
    
    if (!policy.allowedCountries.contains(country)) {
      return false;
    }
    
    if (policy.blockedIPs.contains(ip)) {
      return false;
    }
    
    return true;
  }
  
  // 检查生物识别是否可用
  bool canUseBiometric() {
    return policy.allowBiometric;
  }
  
  // 检查声纹识别是否可用
  bool canUseVoicePrint() {
    return policy.allowVoicePrint;
  }
  
  // 获取声纹匹配阈值
  double getVoicePrintThreshold() {
    return policy.voicePrintThreshold;
  }
  
  // 检查验证码是否在冷却中
  Future<bool> isCodeInCooldown() async {
    final lastSendTime = await _storage.read('last_code_send_time');
    if (lastSendTime == null) return false;
    
    final lastTime = DateTime.parse(lastSendTime);
    final cooldownEnd = lastTime.add(
      Duration(seconds: policy.codeCooldownSeconds),
    );
    
    return DateTime.now().isBefore(cooldownEnd);
  }
  
  // 记录验证码发送
  Future<void> recordCodeSend() async {
    await _storage.write(
      'last_code_send_time',
      DateTime.now().toIso8601String(),
    );
  }
  
  // 检查每日验证码请求次数
  Future<bool> canRequestCode() async {
    final countStr = await _storage.read('today_code_requests');
    final lastDateStr = await _storage.read('last_code_request_date');
    
    final today = DateTime.now().toIso8601String().split('T')[0];
    
    if (lastDateStr != today) {
      // 新的一天，重置计数
      await _storage.write('today_code_requests', '1');
      await _storage.write('last_code_request_date', today);
      return true;
    }
    
    final count = int.parse(countStr ?? '0');
    if (count >= policy.maxDailyCodeRequests) {
      return false;
    }
    
    await _storage.write('today_code_requests', (count + 1).toString());
    return true;
  }
  
  // 更新安全策略
  Future<void> updatePolicy(SecurityPolicy newPolicy) async {
    try {
      await _dioClient.put(
        '/auth/security/policy',
        data: newPolicy.toJson(),
      );
      _policy.value = newPolicy;
    } catch (e) {
      rethrow;
    }
  }
} 