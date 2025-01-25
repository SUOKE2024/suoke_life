class PrivacySettings {
  bool dataEncryptionEnabled;
  bool locationTrackingEnabled;
  bool personalizedAdsEnabled;

  PrivacySettings({
    this.dataEncryptionEnabled = true,
    this.locationTrackingEnabled = false,
    this.personalizedAdsEnabled = false,
  });

  factory PrivacySettings.fromJson(Map<String, dynamic> json) {
    return PrivacySettings(
      dataEncryptionEnabled: json['dataEncryptionEnabled'] ?? true,
      locationTrackingEnabled: json['locationTrackingEnabled'] ?? false,
      personalizedAdsEnabled: json['personalizedAdsEnabled'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'dataEncryptionEnabled': dataEncryptionEnabled,
      'locationTrackingEnabled': locationTrackingEnabled,
      'personalizedAdsEnabled': personalizedAdsEnabled,
    };
  }

  static PrivacySettings defaultSettings() {
    return PrivacySettings();
  }
} 