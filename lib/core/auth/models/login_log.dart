

class LoginLog {
  final String id;
  final String userId;
  final String loginType; // phone, wechat, alipay, biometric, voice
  final String deviceInfo;
  final String ipAddress;
  final String location;
  final bool isSuccess;
  final String? failureReason;
  final DateTime createdAt;
  
  LoginLog({
    required this.id,
    required this.userId,
    required this.loginType,
    required this.deviceInfo,
    required this.ipAddress,
    required this.location,
    required this.isSuccess,
    this.failureReason,
    required this.createdAt,
  });
  
  factory LoginLog.fromJson(Map<String, dynamic> json) => _$LoginLogFromJson(json);
  Map<String, dynamic> toJson() => _$LoginLogToJson(this);
  
  @override
  String toString() {
    return '登录时间：${createdAt.toString()}\n'
           '登录方式：${_getLoginTypeText()}\n'
           '登录设备：$deviceInfo\n'
           '登录地点：$location\n'
           '登录状态：${isSuccess ? '成功' : '失败'}\n'
           '${failureReason != null ? '失败原因：$failureReason\n' : ''}';
  }
  
  String _getLoginTypeText() {
    switch (loginType) {
      case 'phone':
        return '手机验证码';
      case 'wechat':
        return '微信';
      case 'alipay':
        return '支付宝';
      case 'biometric':
        return '生物识别';
      case 'voice':
        return '声纹识别';
      default:
        return '未知';
    }
  }
} 