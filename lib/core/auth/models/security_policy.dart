import 'package:json_annotation/json_annotation.dart';

part 'security_policy.g.dart';

@JsonSerializable()
class SecurityPolicy {
  // 密码策略
  final int minPasswordLength;
  final bool requireSpecialChar;
  final bool requireNumber;
  final bool requireUpperCase;
  final int passwordExpireDays;
  
  // 登录策略
  final int maxLoginAttempts;
  final int lockoutDuration; // 分钟
  final bool requireCaptcha;
  final int captchaThreshold;
  
  // 设备策略
  final int maxDevices;
  final bool allowMultipleDevices;
  final bool trustedDevicesOnly;
  final int deviceTrustExpireDays;
  
  // 位置策略
  final bool locationCheck;
  final List<String> allowedCountries;
  final List<String> blockedIPs;
  
  // 验证码策略
  final int codeLength;
  final int codeExpireMinutes;
  final int codeCooldownSeconds;
  final int maxDailyCodeRequests;
  
  // 会话策略
  final int sessionTimeoutMinutes;
  final bool forceLogoutOnPasswordChange;
  final bool singleSessionOnly;
  
  // 生物识别策略
  final bool allowBiometric;
  final int biometricFailAttempts;
  final int biometricLockoutMinutes;
  
  // 声纹策略
  final bool allowVoicePrint;
  final double voicePrintThreshold;
  final int voicePrintFailAttempts;
  
  SecurityPolicy({
    this.minPasswordLength = 8,
    this.requireSpecialChar = true,
    this.requireNumber = true,
    this.requireUpperCase = true,
    this.passwordExpireDays = 90,
    
    this.maxLoginAttempts = 5,
    this.lockoutDuration = 30,
    this.requireCaptcha = true,
    this.captchaThreshold = 3,
    
    this.maxDevices = 5,
    this.allowMultipleDevices = true,
    this.trustedDevicesOnly = false,
    this.deviceTrustExpireDays = 30,
    
    this.locationCheck = true,
    this.allowedCountries = const ['CN'],
    this.blockedIPs = const [],
    
    this.codeLength = 6,
    this.codeExpireMinutes = 5,
    this.codeCooldownSeconds = 60,
    this.maxDailyCodeRequests = 10,
    
    this.sessionTimeoutMinutes = 30,
    this.forceLogoutOnPasswordChange = true,
    this.singleSessionOnly = false,
    
    this.allowBiometric = true,
    this.biometricFailAttempts = 5,
    this.biometricLockoutMinutes = 30,
    
    this.allowVoicePrint = true,
    this.voicePrintThreshold = 0.85,
    this.voicePrintFailAttempts = 3,
  });
  
  factory SecurityPolicy.fromJson(Map<String, dynamic> json) =>
      _$SecurityPolicyFromJson(json);
  
  Map<String, dynamic> toJson() => _$SecurityPolicyToJson(this);
  
  SecurityPolicy copyWith({
    int? minPasswordLength,
    bool? requireSpecialChar,
    bool? requireNumber,
    bool? requireUpperCase,
    int? passwordExpireDays,
    int? maxLoginAttempts,
    int? lockoutDuration,
    bool? requireCaptcha,
    int? captchaThreshold,
    int? maxDevices,
    bool? allowMultipleDevices,
    bool? trustedDevicesOnly,
    int? deviceTrustExpireDays,
    bool? locationCheck,
    List<String>? allowedCountries,
    List<String>? blockedIPs,
    int? codeLength,
    int? codeExpireMinutes,
    int? codeCooldownSeconds,
    int? maxDailyCodeRequests,
    int? sessionTimeoutMinutes,
    bool? forceLogoutOnPasswordChange,
    bool? singleSessionOnly,
    bool? allowBiometric,
    int? biometricFailAttempts,
    int? biometricLockoutMinutes,
    bool? allowVoicePrint,
    double? voicePrintThreshold,
    int? voicePrintFailAttempts,
  }) {
    return SecurityPolicy(
      minPasswordLength: minPasswordLength ?? this.minPasswordLength,
      requireSpecialChar: requireSpecialChar ?? this.requireSpecialChar,
      requireNumber: requireNumber ?? this.requireNumber,
      requireUpperCase: requireUpperCase ?? this.requireUpperCase,
      passwordExpireDays: passwordExpireDays ?? this.passwordExpireDays,
      maxLoginAttempts: maxLoginAttempts ?? this.maxLoginAttempts,
      lockoutDuration: lockoutDuration ?? this.lockoutDuration,
      requireCaptcha: requireCaptcha ?? this.requireCaptcha,
      captchaThreshold: captchaThreshold ?? this.captchaThreshold,
      maxDevices: maxDevices ?? this.maxDevices,
      allowMultipleDevices: allowMultipleDevices ?? this.allowMultipleDevices,
      trustedDevicesOnly: trustedDevicesOnly ?? this.trustedDevicesOnly,
      deviceTrustExpireDays: deviceTrustExpireDays ?? this.deviceTrustExpireDays,
      locationCheck: locationCheck ?? this.locationCheck,
      allowedCountries: allowedCountries ?? this.allowedCountries,
      blockedIPs: blockedIPs ?? this.blockedIPs,
      codeLength: codeLength ?? this.codeLength,
      codeExpireMinutes: codeExpireMinutes ?? this.codeExpireMinutes,
      codeCooldownSeconds: codeCooldownSeconds ?? this.codeCooldownSeconds,
      maxDailyCodeRequests: maxDailyCodeRequests ?? this.maxDailyCodeRequests,
      sessionTimeoutMinutes: sessionTimeoutMinutes ?? this.sessionTimeoutMinutes,
      forceLogoutOnPasswordChange: forceLogoutOnPasswordChange ?? this.forceLogoutOnPasswordChange,
      singleSessionOnly: singleSessionOnly ?? this.singleSessionOnly,
      allowBiometric: allowBiometric ?? this.allowBiometric,
      biometricFailAttempts: biometricFailAttempts ?? this.biometricFailAttempts,
      biometricLockoutMinutes: biometricLockoutMinutes ?? this.biometricLockoutMinutes,
      allowVoicePrint: allowVoicePrint ?? this.allowVoicePrint,
      voicePrintThreshold: voicePrintThreshold ?? this.voicePrintThreshold,
      voicePrintFailAttempts: voicePrintFailAttempts ?? this.voicePrintFailAttempts,
    );
  }
} 