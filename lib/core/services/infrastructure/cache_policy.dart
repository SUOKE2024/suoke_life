class CachePolicy {
  static bool shouldStoreLocally(String dataType) {
    return [
      PrivacyDataTypes.personalInfo,
      PrivacyDataTypes.healthData,
      PrivacyDataTypes.chatData,
      PrivacyDataTypes.locationData,
      PrivacyDataTypes.behaviorData,
    ].contains(dataType);
  }

  static Duration getRetentionPeriod(String dataType) {
    switch (dataType) {
      case PrivacyDataTypes.chatData:
        return const Duration(days: 30);
      case PrivacyDataTypes.locationData:
        return const Duration(days: 7);
      case PrivacyDataTypes.behaviorData:
        return const Duration(days: 90);
      default:
        return const Duration(days: 365);
    }
  }

  static bool shouldSync(String dataType) {
    // 只同步匿名化后的数据
    return ![
      PrivacyDataTypes.personalInfo,
      PrivacyDataTypes.healthData,
      PrivacyDataTypes.chatData,
    ].contains(dataType);
  }
} 