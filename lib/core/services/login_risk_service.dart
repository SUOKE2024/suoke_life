class LoginRiskService extends GetxService {
  final _storage = Get.find<StorageService>();
  final _deviceInfo = Get.find<DeviceInfoService>();
  
  Future<RiskLevel> assessLoginRisk({
    required String userId,
    required String deviceId,
    required String ipAddress,
    required DateTime timestamp,
  }) async {
    // 1. 检查设备是否可信
    final isTrustedDevice = await _checkTrustedDevice(deviceId);
    
    // 2. 检查IP地址是否异常
    final isUnusualLocation = await _checkUnusualLocation(ipAddress);
    
    // 3. 检查登录时间是否异常
    final isUnusualTime = _checkUnusualTime(timestamp);
    
    // 4. 检查最近失败次数
    final recentFailures = await _getRecentFailures(userId);

    // 根据各项指标计算风险等级
    return _calculateRiskLevel(
      isTrustedDevice: isTrustedDevice,
      isUnusualLocation: isUnusualLocation,
      isUnusualTime: isUnusualTime,
      recentFailures: recentFailures,
    );
  }

  Future<bool> _checkTrustedDevice(String deviceId) async {
    final trustedDevices = await _storage.getStringList('trusted_devices') ?? [];
    return trustedDevices.contains(deviceId);
  }

  Future<bool> _checkUnusualLocation(String ipAddress) async {
    // 获取IP地址的地理位置信息
    final location = await _getIpLocation(ipAddress);
    
    // 获取用户常用登录地点
    final usualLocations = await _storage.getStringList('usual_locations') ?? [];
    
    // 检查是否是异常地点
    return !usualLocations.contains(location.city);
  }

  bool _checkUnusualTime(DateTime timestamp) {
    final hour = timestamp.hour;
    // 假设正常登录时间为6:00-23:00
    return hour < 6 || hour > 23;
  }

  Future<int> _getRecentFailures(String userId) async {
    final key = 'login_failures_$userId';
    final failures = await _storage.getStringList(key) ?? [];
    
    // 只统计最近30分钟内的失败次数
    final recentFailures = failures.where((time) {
      final failureTime = DateTime.parse(time);
      return DateTime.now().difference(failureTime) <= const Duration(minutes: 30);
    }).length;
    
    return recentFailures;
  }

  RiskLevel _calculateRiskLevel({
    required bool isTrustedDevice,
    required bool isUnusualLocation,
    required bool isUnusualTime,
    required int recentFailures,
  }) {
    int riskScore = 0;
    
    if (!isTrustedDevice) riskScore += 2;
    if (isUnusualLocation) riskScore += 3;
    if (isUnusualTime) riskScore += 1;
    riskScore += recentFailures;

    if (riskScore >= 5) return RiskLevel.high;
    if (riskScore >= 3) return RiskLevel.medium;
    return RiskLevel.low;
  }
} 