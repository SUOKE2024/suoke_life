// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'security_policy.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SecurityPolicy _$SecurityPolicyFromJson(Map<String, dynamic> json) =>
    SecurityPolicy(
      minPasswordLength: (json['minPasswordLength'] as num?)?.toInt() ?? 8,
      requireSpecialChar: json['requireSpecialChar'] as bool? ?? true,
      requireNumber: json['requireNumber'] as bool? ?? true,
      requireUpperCase: json['requireUpperCase'] as bool? ?? true,
      passwordExpireDays: (json['passwordExpireDays'] as num?)?.toInt() ?? 90,
      maxLoginAttempts: (json['maxLoginAttempts'] as num?)?.toInt() ?? 5,
      lockoutDuration: (json['lockoutDuration'] as num?)?.toInt() ?? 30,
      requireCaptcha: json['requireCaptcha'] as bool? ?? true,
      captchaThreshold: (json['captchaThreshold'] as num?)?.toInt() ?? 3,
      maxDevices: (json['maxDevices'] as num?)?.toInt() ?? 5,
      allowMultipleDevices: json['allowMultipleDevices'] as bool? ?? true,
      trustedDevicesOnly: json['trustedDevicesOnly'] as bool? ?? false,
      deviceTrustExpireDays:
          (json['deviceTrustExpireDays'] as num?)?.toInt() ?? 30,
      locationCheck: json['locationCheck'] as bool? ?? true,
      allowedCountries: (json['allowedCountries'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const ['CN'],
      blockedIPs: (json['blockedIPs'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      codeLength: (json['codeLength'] as num?)?.toInt() ?? 6,
      codeExpireMinutes: (json['codeExpireMinutes'] as num?)?.toInt() ?? 5,
      codeCooldownSeconds: (json['codeCooldownSeconds'] as num?)?.toInt() ?? 60,
      maxDailyCodeRequests:
          (json['maxDailyCodeRequests'] as num?)?.toInt() ?? 10,
      sessionTimeoutMinutes:
          (json['sessionTimeoutMinutes'] as num?)?.toInt() ?? 30,
      forceLogoutOnPasswordChange:
          json['forceLogoutOnPasswordChange'] as bool? ?? true,
      singleSessionOnly: json['singleSessionOnly'] as bool? ?? false,
      allowBiometric: json['allowBiometric'] as bool? ?? true,
      biometricFailAttempts:
          (json['biometricFailAttempts'] as num?)?.toInt() ?? 5,
      biometricLockoutMinutes:
          (json['biometricLockoutMinutes'] as num?)?.toInt() ?? 30,
      allowVoicePrint: json['allowVoicePrint'] as bool? ?? true,
      voicePrintThreshold:
          (json['voicePrintThreshold'] as num?)?.toDouble() ?? 0.85,
      voicePrintFailAttempts:
          (json['voicePrintFailAttempts'] as num?)?.toInt() ?? 3,
    );

Map<String, dynamic> _$SecurityPolicyToJson(SecurityPolicy instance) =>
    <String, dynamic>{
      'minPasswordLength': instance.minPasswordLength,
      'requireSpecialChar': instance.requireSpecialChar,
      'requireNumber': instance.requireNumber,
      'requireUpperCase': instance.requireUpperCase,
      'passwordExpireDays': instance.passwordExpireDays,
      'maxLoginAttempts': instance.maxLoginAttempts,
      'lockoutDuration': instance.lockoutDuration,
      'requireCaptcha': instance.requireCaptcha,
      'captchaThreshold': instance.captchaThreshold,
      'maxDevices': instance.maxDevices,
      'allowMultipleDevices': instance.allowMultipleDevices,
      'trustedDevicesOnly': instance.trustedDevicesOnly,
      'deviceTrustExpireDays': instance.deviceTrustExpireDays,
      'locationCheck': instance.locationCheck,
      'allowedCountries': instance.allowedCountries,
      'blockedIPs': instance.blockedIPs,
      'codeLength': instance.codeLength,
      'codeExpireMinutes': instance.codeExpireMinutes,
      'codeCooldownSeconds': instance.codeCooldownSeconds,
      'maxDailyCodeRequests': instance.maxDailyCodeRequests,
      'sessionTimeoutMinutes': instance.sessionTimeoutMinutes,
      'forceLogoutOnPasswordChange': instance.forceLogoutOnPasswordChange,
      'singleSessionOnly': instance.singleSessionOnly,
      'allowBiometric': instance.allowBiometric,
      'biometricFailAttempts': instance.biometricFailAttempts,
      'biometricLockoutMinutes': instance.biometricLockoutMinutes,
      'allowVoicePrint': instance.allowVoicePrint,
      'voicePrintThreshold': instance.voicePrintThreshold,
      'voicePrintFailAttempts': instance.voicePrintFailAttempts,
    };
