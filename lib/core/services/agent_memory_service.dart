import 'package:sqflite/sqflite.dart';
import 'package:suoke_life/lib/core/config/database_config.dart';
import 'package:suoke_life/lib/core/config/app_config.dart';
import 'package:suoke_life/lib/core/models/conversation_summary.dart';
import 'package:suoke_life/lib/core/models/conversation_turn.dart';
import 'package:suoke_life/lib/core/models/user_preference.dart';
import 'package:suoke_life/lib/core/services/infrastructure/local_storage_service.dart';

abstract class AgentMemoryService {
  // 存储对话轮次
  Future<void> saveConversationTurn(ConversationTurn turn);

  // 获取指定 Agent 的对话历史
  Future<List<ConversationTurn>> getConversationHistory({
    required String userId,
    required String agentId,
    int? limit,
  });

  // 清空指定 Agent 的对话历史
  Future<void> clearConversationHistory({
    required String userId,
    required String agentId,
  });

  // 存储用户偏好
  Future<void> saveUserPreference(UserPreference preference);

  // 获取用户偏好
  Future<UserPreference?> getUserPreference({
    required String userId,
    required String agentId,
    required String key,
  });

  // 获取所有用户偏好
  Future<List<UserPreference>> getAllUserPreferences({
    required String userId,
    required String agentId,
  });

  // 删除用户偏好
  Future<void> deleteUserPreference({
    required String userId,
    required String agentId,
    required String key,
  });

  // 清理过期数据
  Future<void> cleanUpExpiredData(String userId);
}

class AgentMemoryServiceImpl implements AgentMemoryService {
  final LocalStorageService _localStorageService;
  final AppConfig _appConfig;
  final DatabaseConfig _databaseConfig;

  AgentMemoryServiceImpl(
    this._localStorageService,
    this._appConfig,
    this._databaseConfig,
  );

  static const String _conversationTurnsTable = 'conversation_turns'; // 对话轮次表名
  static const String _userPreferencesTable = 'user_preferences'; // 用户偏好表名
  static const String _conversationSummaryTable = 'conversation_summaries';

  @override
  Future<void> saveConversationTurn(ConversationTurn turn) async {
    await _localStorageService.insert(_conversationTurnsTable, turn.toMap());
  }

  @override
  Future<List<ConversationTurn>> getConversationHistory({
    required String userId,
    required String agentId,
    int? limit,
  }) async {
    final List<Map<String, dynamic>> maps = await _localStorageService.query(
      _conversationTurnsTable,
      where: 'userId = ? AND agentId = ?',
      whereArgs: [userId, agentId],
    );
    return maps.map((map) => ConversationTurn.fromMap(map)).toList();
  }

  @override
  Future<void> clearConversationHistory({
    required String userId,
    required String agentId,
  }) async {
    await _localStorageService.delete(
      _conversationTurnsTable,
      where: 'userId = ? AND agentId = ?',
      whereArgs: [userId, agentId],
    );
  }

  @override
  Future<void> saveUserPreference(UserPreference preference) async {
    await _localStorageService.insert(
        _userPreferencesTable, preference.toMap());
  }

  @override
  Future<UserPreference?> getUserPreference({
    required String userId,
    required String agentId,
    required String key,
  }) async {
    final List<Map<String, dynamic>> maps = await _localStorageService.query(
      _userPreferencesTable,
      where: 'userId = ? AND agentId = ? AND key = ?',
      whereArgs: [userId, agentId, key],
    );
    if (maps.isEmpty) {
      return null;
    }
    return UserPreference.fromMap(maps.first); // 假设 key 是唯一的，返回第一个结果
  }

  @override
  Future<List<UserPreference>> getAllUserPreferences({
    required String userId,
    required String agentId,
  }) async {
    final List<Map<String, dynamic>> maps = await _localStorageService.query(
      _userPreferencesTable,
      where: 'userId = ? AND agentId = ?',
      whereArgs: [userId, agentId],
    );
    return maps.map((map) => UserPreference.fromMap(map)).toList();
  }

  @override
  Future<void> deleteUserPreference({
    required String userId,
    required String agentId,
    required String key,
  }) async {
    await _localStorageService.delete(
      _userPreferencesTable,
      where: 'userId = ? AND agentId = ? AND key = ?',
      whereArgs: [userId, agentId, key],
    );
  }

  @override
  Future<void> cleanUpExpiredData(String userId) async {
    print('开始清理过期数据, User ID: $userId'); //  添加日志
    final db = await _databaseConfig.database;
    final userPreference = await getUserPreference(userId);
    final retentionPeriod = userPreference?.localDataRetentionPeriod ??
        _appConfig
            .defaultLocalDataRetentionPeriod; //  从 UserPreference 或 AppConfig 获取保留期限
    if (retentionPeriod == 'persistent') {
      print('数据保留策略设置为永久保留，跳过清理'); //  添加日志
      return; // 永久保留，无需清理
    }

    Duration duration;
    switch (retentionPeriod) {
      case '7d':
        duration = const Duration(days: 7);
        break;
      case '30d':
        duration = const Duration(days: 30);
        break;
      case '90d':
        duration = const Duration(days: 90);
        break;
      default:
        duration = const Duration(days: 30); // 默认 30 天
    }

    final expiryDate = DateTime.now().subtract(duration);
    final expiryTimestamp = expiryDate.millisecondsSinceEpoch;

    print('数据保留期限: $retentionPeriod, 过期时间戳: $expiryTimestamp'); //  添加日志

    // 清理对话历史
    int deletedConversationTurns = await db.delete(
      _conversationTurnsTable,
      where: 'userId = ? AND timestamp < ?',
      whereArgs: [userId, expiryTimestamp],
    );
    print('清理对话历史，删除 $deletedConversationTurns 条记录'); //  添加日志

    //  清理用户偏好设置 (如果需要定期清理用户偏好，可以添加类似代码)
    // int deletedUserPreferences = await db.delete(
    //   _userPreferencesTable,
    //   where: 'userId = ? AND timestamp < ?', //  假设 UserPreference 也有 timestamp 字段
    //   whereArgs: [userId, expiryTimestamp],
    // );
    // print('清理用户偏好设置，删除 ${deletedUserPreferences} 条记录'); //  添加日志

    // 清理对话总结
    int deletedConversationSummaries = await db.delete(
      _conversationSummaryTable,
      where: 'userId = ? AND timestamp < ?',
      whereArgs: [userId, expiryTimestamp],
    );
    print('清理对话总结，删除 $deletedConversationSummaries 条记录'); //  添加日志

    print('过期数据清理完成'); //  添加日志
  }
}
