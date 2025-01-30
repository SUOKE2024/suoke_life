class DeviceInfo {
  final String id;
  final String userId;
  final String deviceName;
  final String deviceModel;
  final String osVersion;
  final String appVersion;
  final DateTime lastLoginAt;
  final bool isCurrentDevice;
  final Map<String, dynamic>? metadata;

  const DeviceInfo({
    required this.id,
    required this.userId,
    required this.deviceName,
    required this.deviceModel,
    required this.osVersion,
    required this.appVersion,
    required this.lastLoginAt,
    this.isCurrentDevice = false,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'user_id': userId,
    'device_name': deviceName,
    'device_model': deviceModel,
    'os_version': osVersion,
    'app_version': appVersion,
    'last_login_at': lastLoginAt.toIso8601String(),
    'is_current_device': isCurrentDevice,
    'metadata': metadata,
  };

  factory DeviceInfo.fromJson(Map<String, dynamic> json) => DeviceInfo(
    id: json['id'],
    userId: json['user_id'],
    deviceName: json['device_name'],
    deviceModel: json['device_model'],
    osVersion: json['os_version'],
    appVersion: json['app_version'],
    lastLoginAt: DateTime.parse(json['last_login_at']),
    isCurrentDevice: json['is_current_device'] ?? false,
    metadata: json['metadata'],
  );
} 