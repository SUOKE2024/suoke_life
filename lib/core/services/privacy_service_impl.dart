import 'package:crypto/crypto.dart';
import 'dart:convert';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/core/services/privacy_service.dart';
import 'package:uuid/uuid.dart';
import 'package:suoke_life/core/models/privacy_settings.dart';

class PrivacyServiceImpl implements PrivacyService {
  final LocalStorageService _localStorageService;
  final String _userIdKey = 'user_id';
  final String _privacySettingsKey = 'privacy_settings';

  PrivacyServiceImpl(this._localStorageService);

  @override
  Future<String> getUserId() async {
    String? userId = await _localStorageService.getStringValue(_userIdKey);
    if (userId == null) {
      userId = const Uuid().v4();
      print('Generated new userId: $userId');
      await _localStorageService.setStringValue(_userIdKey, userId);
    }
    return userId;
  }

  @override
  Future<PrivacySettings> getPrivacySettings() async {
    final settingsJson = await _localStorageService.getString(_privacySettingsKey);
    if (settingsJson != null) {
      return PrivacySettings.fromJson(jsonDecode(settingsJson));
    }
    return PrivacySettings.defaultSettings();
  }

  @override
  Future<void> updatePrivacySettings(PrivacySettings settings) async {
    final settingsJson = jsonEncode(settings.toJson());
    await _localStorageService.setString(_privacySettingsKey, settingsJson);
  }

  @override
  Future<void> setPrivacySettings(Map<String, dynamic> settings) async {
    final settingsJson = jsonEncode(settings);
    print('Saving privacy settings from map: $settingsJson');
    await _localStorageService.setStringValue(_privacySettingsKey, settingsJson);
  }

  @override
  Future<void> anonymizeData() async {
    // TODO: Implement data anonymization logic
    // Example:
    // final userId = await getUserId();
    // final anonymizedUserId = sha256Hash(userId);
    // await _localStorageService.save('anonymized_user_id', anonymizedUserId);
  }

  @override
  Future<void> clearPrivacyData() async {
    // TODO: Implement clear privacy data logic
    // Example:
    // await _localStorageService.delete('anonymized_user_id');
  }

  @override
  Future<Map<String, dynamic>> anonymizeUserData(Map<String, dynamic> userData) async {
    final userId = await getUserId();
    final anonymizedData = Map<String, dynamic>.from(userData);

    if (anonymizedData.containsKey('id')) {
      anonymizedData['id'] = sha256.convert(utf8.encode(userId)).toString();
    }
    if (anonymizedData.containsKey('name')) {
      anonymizedData['name'] = _maskName(anonymizedData['name']);
    }
    if (anonymizedData.containsKey('email')) {
      anonymizedData['email'] = _maskEmail(anonymizedData['email']);
    }
    if (anonymizedData.containsKey('phone_number')) {
      anonymizedData['phone_number'] = _maskPhoneNumber(anonymizedData['phone_number']);
    }
    if (anonymizedData.containsKey('address')) {
      anonymizedData['address'] = _maskAddress(anonymizedData['address']);
    }
    if (anonymizedData.containsKey('location')) {
      anonymizedData['location'] = _anonymizeLocation(anonymizedData['location']);
    }
    return anonymizedData;
  }

  String _maskName(String name) {
    if (name.length > 2) {
      return '${name[0]}${'*' * (name.length - 2)}${name[name.length - 1]}';
    } else {
      return '*' * name.length;
    }
  }

  String _maskEmail(String email) {
    final parts = email.split('@');
    if (parts.length == 2) {
      final username = parts[0];
      final domain = parts[1];
      if (username.length > 2) {
        return '${username[0]}${'*' * (username.length - 2)}${username[username.length - 1]}@$domain';
      } else {
        return '*' * username.length + '@$domain';
      }
    } else {
      return email;
    }
  }

  String _maskPhoneNumber(String phoneNumber) {
    if (phoneNumber.length > 4) {
      return '${phoneNumber.substring(0, 3)}${'*' * (phoneNumber.length - 6)}${phoneNumber.substring(phoneNumber.length - 3)}';
    } else {
      return '*' * phoneNumber.length;
    }
  }

  String _maskAddress(String address) {
    final parts = address.split(',');
    if (parts.isNotEmpty) {
      return '${parts[0]}, ${'*' * 5}';
    } else {
      return address;
    }
  }

  String _anonymizeLocation(String location) {
    return 'City Level';
  }
} 