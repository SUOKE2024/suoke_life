import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite/sqflite.dart';
import '../api/api_service.dart';
import '../../data/local/database/database_helper.dart';

class ChatSettingsService extends GetxService {
  static const _notificationsKey = 'chat_notifications_enabled';
  static const _soundKey = 'chat_sound_enabled';
  
  final _prefs = Get.find<SharedPreferences>();
  final _api = Get.find<ApiService>();
  final _dbHelper = DatabaseHelper();
  
  Future<bool> getNotificationsEnabled() async {
    return _prefs.getBool(_notificationsKey) ?? true;
  }

  Future<void> setNotificationsEnabled(bool enabled) async {
    await _prefs.setBool(_notificationsKey, enabled);
    // 同步到服务器
    try {
      await _api.post('/settings/notifications', data: {
        'enabled': enabled,
      });
    } catch (e) {
      print('同步通知设置失败: $e');
    }
  }

  Future<bool> getSoundEnabled() async {
    return _prefs.getBool(_soundKey) ?? true;
  }

  Future<void> setSoundEnabled(bool enabled) async {
    await _prefs.setBool(_soundKey, enabled);
    // 同步到服务器
    try {
      await _api.post('/settings/sound', data: {
        'enabled': enabled,
      });
    } catch (e) {
      print('同步声音设置失败: $e');
    }
  }

  Future<void> clearChatHistory() async {
    final db = await _dbHelper.database;
    await db.delete('messages');
    // 同步到服务器
    try {
      await _api.delete('/chat/history');
    } catch (e) {
      print('同步清空聊天记录失败: $e');
    }
  }

  Future<ChatSettings> getSettings() async {
    return ChatSettings(
      notificationsEnabled: await getNotificationsEnabled(),
      soundEnabled: await getSoundEnabled(),
    );
  }

  Future<void> saveSettings(ChatSettings settings) async {
    await setNotificationsEnabled(settings.notificationsEnabled);
    await setSoundEnabled(settings.soundEnabled);
  }
}

class ChatSettings {
  final bool notificationsEnabled;
  final bool soundEnabled;

  ChatSettings({
    required this.notificationsEnabled,
    required this.soundEnabled,
  });
} 