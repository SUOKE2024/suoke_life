class AppSettings {
  final String language;
  final String theme;
  final bool notificationsEnabled;
  final bool biometricEnabled;
  final Map<String, bool> privacySettings;
  final Map<String, dynamic> preferences;

  AppSettings({
    required this.language,
    required this.theme,
    required this.notificationsEnabled,
    required this.biometricEnabled,
    required this.privacySettings,
    required this.preferences,
  });

  Map<String, dynamic> toMap() => {
    'language': language,
    'theme': theme,
    'notificationsEnabled': notificationsEnabled,
    'biometricEnabled': biometricEnabled,
    'privacySettings': privacySettings,
    'preferences': preferences,
  };

  factory AppSettings.fromMap(Map<String, dynamic> map) => AppSettings(
    language: map['language'] ?? 'zh_CN',
    theme: map['theme'] ?? 'system',
    notificationsEnabled: map['notificationsEnabled'] ?? true,
    biometricEnabled: map['biometricEnabled'] ?? false,
    privacySettings: Map<String, bool>.from(map['privacySettings'] ?? {}),
    preferences: map['preferences'] ?? {},
  );

  AppSettings copyWith({
    String? language,
    String? theme,
    bool? notificationsEnabled,
    bool? biometricEnabled,
    Map<String, bool>? privacySettings,
    Map<String, dynamic>? preferences,
  }) => AppSettings(
    language: language ?? this.language,
    theme: theme ?? this.theme,
    notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
    biometricEnabled: biometricEnabled ?? this.biometricEnabled,
    privacySettings: privacySettings ?? this.privacySettings,
    preferences: preferences ?? this.preferences,
  );
} 