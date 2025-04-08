/// 可疑登录尝试
class SuspiciousLoginAttempt {
  /// 尝试ID
  final String id;
  
  /// 尝试时间
  final DateTime timestamp;
  
  /// IP地址
  final String ipAddress;
  
  /// 设备信息
  final String deviceInfo;
  
  /// 位置信息
  final String? location;
  
  /// 异常原因
  final String reason;
  
  /// 是否已处理
  final bool isResolved;
  
  /// 风险级别 (0-100)
  final int riskLevel;
  
  SuspiciousLoginAttempt({
    required this.id,
    required this.timestamp,
    required this.ipAddress,
    required this.deviceInfo,
    this.location,
    required this.reason,
    this.isResolved = false,
    required this.riskLevel,
  });
  
  /// 判断是否为高风险尝试
  bool get isHighRisk => riskLevel >= 75;
  
  /// 判断是否为中等风险尝试
  bool get isMediumRisk => riskLevel >= 50 && riskLevel < 75;
  
  /// 判断是否为低风险尝试
  bool get isLowRisk => riskLevel < 50;
  
  /// 判断是否需要紧急处理
  bool get needsUrgentAction => isHighRisk && !isResolved;
} 