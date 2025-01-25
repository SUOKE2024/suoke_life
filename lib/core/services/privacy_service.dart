import 'package:suoke_life/core/models/privacy_settings.dart';

abstract class PrivacyService {
  Future<String> getUserId();
  Future<PrivacySettings> getPrivacySettings();
  Future<void> updatePrivacySettings(PrivacySettings settings);
  Future<void> setPrivacySettings(Map<String, dynamic> settings);
  Future<void> anonymizeData();
  Future<void> clearPrivacyData();
  Future<Map<String, dynamic>> anonymizeUserData(Map<String, dynamic> userData);
} 