import 'dart:convert';
import 'package:logger/logger.dart';
import '../../models/user_data.dart';
import '../../local/dao/user_data_dao.dart';
import '../interfaces/user_data_repository.dart';
import 'base_repository_impl.dart';

/// 用户数据仓库实现
class UserDataRepositoryImpl extends BaseRepositoryImpl<UserData>
    implements UserDataRepository {
  final UserDataDao _dao;
  final Logger _logger = Logger();

  static const String _settingsKey = 'user_settings';
  static const String _preferencesKey = 'user_preferences';

  UserDataRepositoryImpl(this._dao) : super(_dao);

  @override
  Future<String?> getValue(String key) async {
    try {
      return await _dao.getValue(key);
    } catch (e) {
      _logger.e('Error getting value for key $key: $e');
      rethrow;
    }
  }

  @override
  Future<void> setValue(String key, String value) async {
    try {
      await _dao.setValue(key, value);
    } catch (e) {
      _logger.e('Error setting value for key $key: $e');
      rethrow;
    }
  }

  @override
  Future<void> removeValue(String key) async {
    try {
      await _dao.removeValue(key);
    } catch (e) {
      _logger.e('Error removing value for key $key: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getAllKeys() async {
    try {
      return await _dao.getAllKeys();
    } catch (e) {
      _logger.e('Error getting all keys: $e');
      rethrow;
    }
  }

  @override
  Future<void> clear() async {
    try {
      await _dao.clear();
    } catch (e) {
      _logger.e('Error clearing user data: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, String>> getValues(List<String> keys) async {
    try {
      return await _dao.getValues(keys);
    } catch (e) {
      _logger.e('Error getting values for keys $keys: $e');
      rethrow;
    }
  }

  @override
  Future<void> setValues(Map<String, String> values) async {
    try {
      await _dao.setValues(values);
    } catch (e) {
      _logger.e('Error setting multiple values: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, dynamic>> getSettings() async {
    try {
      final settingsJson = await getValue(_settingsKey);
      if (settingsJson == null) return {};
      return json.decode(settingsJson) as Map<String, dynamic>;
    } catch (e) {
      _logger.e('Error getting user settings: $e');
      return {};
    }
  }

  @override
  Future<void> updateSettings(Map<String, dynamic> settings) async {
    try {
      final settingsJson = json.encode(settings);
      await setValue(_settingsKey, settingsJson);
    } catch (e) {
      _logger.e('Error updating user settings: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, dynamic>> getPreferences() async {
    try {
      final preferencesJson = await getValue(_preferencesKey);
      if (preferencesJson == null) return {};
      return json.decode(preferencesJson) as Map<String, dynamic>;
    } catch (e) {
      _logger.e('Error getting user preferences: $e');
      return {};
    }
  }

  @override
  Future<void> updatePreferences(Map<String, dynamic> preferences) async {
    try {
      final preferencesJson = json.encode(preferences);
      await setValue(_preferencesKey, preferencesJson);
    } catch (e) {
      _logger.e('Error updating user preferences: $e');
      rethrow;
    }
  }
} 