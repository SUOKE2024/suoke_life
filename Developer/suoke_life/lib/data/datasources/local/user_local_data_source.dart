import 'dart:convert';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/entities/user_preferences.dart';
import 'package:suoke_life/domain/entities/user_profile.dart';
import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/data/models/user_preferences_model.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite/sqflite.dart';

/// 用户本地数据源接口
abstract class UserLocalDataSource {
  /// 获取用户访问令牌
  Future<String> getAccessToken();
  
  /// 获取用户信息
  Future<User> getUser(String userId);
  
  /// 缓存用户信息
  Future<void> cacheUser(User user);
  
  /// 获取用户个人资料
  Future<UserProfile> getUserProfile(String userId);
  
  /// 缓存用户个人资料
  Future<void> cacheUserProfile(UserProfile profile);
  
  /// 获取用户偏好设置
  Future<UserPreferences> getUserPreferences(String userId);
  
  /// 缓存用户偏好设置
  Future<void> cacheUserPreferences(UserPreferences preferences);
  
  /// 获取用户知识偏好
  Future<Map<String, dynamic>> getUserKnowledgePreferences(String userId);
  
  /// 缓存用户知识偏好
  Future<void> cacheUserKnowledgePreferences(String userId, Map<String, dynamic> knowledgePreferences);
  
  /// 获取用户健康档案
  Future<Map<String, dynamic>> getUserHealthProfile(String userId);
  
  /// 缓存用户健康档案
  Future<void> cacheUserHealthProfile(String userId, Map<String, dynamic> healthProfile);
  
  /// 获取用户浏览历史
  Future<List<Map<String, dynamic>>> getUserViewHistory(String userId, {int limit = 10, int offset = 0});
  
  /// 记录用户内容浏览
  Future<void> recordContentView(String userId, String contentId);
  
  /// 缓存用户浏览历史
  Future<void> cacheUserViewHistory(String userId, List<Map<String, dynamic>> viewHistory);
  
  /// 获取用户收藏内容
  Future<List<Map<String, dynamic>>> getUserFavorites(String userId, {int limit = 10, int offset = 0});
  
  /// 添加内容到收藏
  Future<void> addToFavorites(String userId, String contentId);
  
  /// 从收藏中移除内容
  Future<void> removeFromFavorites(String userId, String contentId);
  
  /// 缓存用户收藏内容
  Future<void> cacheUserFavorites(String userId, List<Map<String, dynamic>> favorites);
  
  /// 获取用户社交分享
  Future<List<Map<String, dynamic>>> getUserSocialShares(String userId, {int limit = 10, int offset = 0});
  
  /// 缓存用户社交分享
  Future<void> cacheUserSocialShares(String userId, List<Map<String, dynamic>> socialShares);
  
  /// 缓存单个社交分享
  Future<void> cacheSocialShare(String userId, Map<String, dynamic> socialShare);
}

/// 用户本地数据源实现
class UserLocalDataSourceImpl implements UserLocalDataSource {
  final SharedPreferences _sharedPreferences;
  final Database _database;
  
  /// 缓存键前缀
  static const String _userCachePrefix = 'CACHED_USER_';
  static const String _userProfileCachePrefix = 'CACHED_USER_PROFILE_';
  static const String _userPrefsCachePrefix = 'CACHED_USER_PREFS_';
  static const String _knowledgePrefsCachePrefix = 'CACHED_KNOWLEDGE_PREFS_';
  static const String _healthProfileCachePrefix = 'CACHED_HEALTH_PROFILE_';
  static const String _accessTokenKey = 'ACCESS_TOKEN';
  
  UserLocalDataSourceImpl({
    required SharedPreferences sharedPreferences,
    required Database database,
  })  : _sharedPreferences = sharedPreferences,
        _database = database;
  
  @override
  Future<String> getAccessToken() async {
    final token = _sharedPreferences.getString(_accessTokenKey);
    if (token != null) {
      return token;
    } else {
      throw CacheException(message: '无法获取访问令牌');
    }
  }
  
  @override
  Future<User> getUser(String userId) async {
    final jsonString = _sharedPreferences.getString(_userCachePrefix + userId);
    if (jsonString != null) {
      return UserModel.fromJson(json.decode(jsonString));
    } else {
      throw CacheException(message: '用户数据未缓存');
    }
  }
  
  @override
  Future<void> cacheUser(User user) async {
    final userModel = user is UserModel ? user : UserModel.fromUser(user);
    await _sharedPreferences.setString(
      _userCachePrefix + user.id,
      json.encode(userModel.toJson()),
    );
  }
  
  @override
  Future<UserProfile> getUserProfile(String userId) async {
    final jsonString = _sharedPreferences.getString(_userProfileCachePrefix + userId);
    if (jsonString != null) {
      return UserProfile.fromJson(json.decode(jsonString));
    } else {
      throw CacheException(message: '用户个人资料未缓存');
    }
  }
  
  @override
  Future<void> cacheUserProfile(UserProfile profile) async {
    await _sharedPreferences.setString(
      _userProfileCachePrefix + profile.id,
      json.encode(profile.toJson()),
    );
  }
  
  @override
  Future<UserPreferences> getUserPreferences(String userId) async {
    final jsonString = _sharedPreferences.getString(_userPrefsCachePrefix + userId);
    if (jsonString != null) {
      return UserPreferencesModel.fromJson(json.decode(jsonString));
    } else {
      throw CacheException(message: '用户偏好设置未缓存');
    }
  }
  
  @override
  Future<void> cacheUserPreferences(UserPreferences preferences) async {
    final preferencesModel = preferences is UserPreferencesModel
        ? preferences
        : UserPreferencesModel.fromUserPreferences(preferences);
    await _sharedPreferences.setString(
      _userPrefsCachePrefix + preferences.userId,
      json.encode(preferencesModel.toJson()),
    );
  }
  
  @override
  Future<Map<String, dynamic>> getUserKnowledgePreferences(String userId) async {
    final jsonString = _sharedPreferences.getString(_knowledgePrefsCachePrefix + userId);
    if (jsonString != null) {
      return json.decode(jsonString);
    } else {
      throw CacheException(message: '用户知识偏好未缓存');
    }
  }
  
  @override
  Future<void> cacheUserKnowledgePreferences(String userId, Map<String, dynamic> knowledgePreferences) async {
    await _sharedPreferences.setString(
      _knowledgePrefsCachePrefix + userId,
      json.encode(knowledgePreferences),
    );
  }
  
  @override
  Future<Map<String, dynamic>> getUserHealthProfile(String userId) async {
    final jsonString = _sharedPreferences.getString(_healthProfileCachePrefix + userId);
    if (jsonString != null) {
      return json.decode(jsonString);
    } else {
      throw CacheException(message: '用户健康档案未缓存');
    }
  }
  
  @override
  Future<void> cacheUserHealthProfile(String userId, Map<String, dynamic> healthProfile) async {
    await _sharedPreferences.setString(
      _healthProfileCachePrefix + userId,
      json.encode(healthProfile),
    );
  }
  
  @override
  Future<List<Map<String, dynamic>>> getUserViewHistory(String userId, {int limit = 10, int offset = 0}) async {
    try {
      final results = await _database.query(
        'user_view_history',
        where: 'user_id = ?',
        whereArgs: [userId],
        orderBy: 'view_date DESC',
        limit: limit,
        offset: offset,
      );
      
      return results.map((row) => {
        'contentId': row['content_id'] as String,
        'title': row['title'] as String,
        'viewDate': row['view_date'] as String,
        'contentType': row['content_type'] as String,
        'thumbnailUrl': row['thumbnail_url'] as String?,
      }).toList();
    } catch (e) {
      throw CacheException(message: '获取用户浏览历史失败: $e');
    }
  }
  
  @override
  Future<void> recordContentView(String userId, String contentId) async {
    try {
      // 首先检查是否已存在相同记录
      final existingRecord = await _database.query(
        'user_view_history',
        where: 'user_id = ? AND content_id = ?',
        whereArgs: [userId, contentId],
      );
      
      if (existingRecord.isNotEmpty) {
        // 如果已存在，则更新时间戳
        await _database.update(
          'user_view_history',
          {'view_date': DateTime.now().toIso8601String()},
          where: 'user_id = ? AND content_id = ?',
          whereArgs: [userId, contentId],
        );
      } else {
        // 从内容表获取内容信息
        final contentInfo = await _database.query(
          'contents',
          where: 'id = ?',
          whereArgs: [contentId],
        );
        
        if (contentInfo.isNotEmpty) {
          // 添加新记录
          await _database.insert(
            'user_view_history',
            {
              'user_id': userId,
              'content_id': contentId,
              'title': contentInfo.first['title'],
              'view_date': DateTime.now().toIso8601String(),
              'content_type': contentInfo.first['content_type'],
              'thumbnail_url': contentInfo.first['thumbnail_url'],
            },
          );
        } else {
          // 如果内容信息不存在，则仅记录ID和时间
          await _database.insert(
            'user_view_history',
            {
              'user_id': userId,
              'content_id': contentId,
              'title': '未知内容',
              'view_date': DateTime.now().toIso8601String(),
              'content_type': 'unknown',
              'thumbnail_url': null,
            },
          );
        }
      }
    } catch (e) {
      throw CacheException(message: '记录内容浏览失败: $e');
    }
  }
  
  @override
  Future<void> cacheUserViewHistory(String userId, List<Map<String, dynamic>> viewHistory) async {
    try {
      // 开始事务
      await _database.transaction((txn) async {
        // 清除该用户的所有历史记录
        await txn.delete(
          'user_view_history',
          where: 'user_id = ?',
          whereArgs: [userId],
        );
        
        // 插入新的历史记录
        for (var item in viewHistory) {
          await txn.insert(
            'user_view_history',
            {
              'user_id': userId,
              'content_id': item['contentId'],
              'title': item['title'],
              'view_date': item['viewDate'],
              'content_type': item['contentType'],
              'thumbnail_url': item['thumbnailUrl'],
            },
          );
        }
      });
    } catch (e) {
      throw CacheException(message: '缓存用户浏览历史失败: $e');
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> getUserFavorites(String userId, {int limit = 10, int offset = 0}) async {
    try {
      final results = await _database.query(
        'user_favorites',
        where: 'user_id = ?',
        whereArgs: [userId],
        orderBy: 'added_date DESC',
        limit: limit,
        offset: offset,
      );
      
      return results.map((row) => {
        'contentId': row['content_id'] as String,
        'title': row['title'] as String,
        'addedDate': row['added_date'] as String,
        'contentType': row['content_type'] as String,
        'thumbnailUrl': row['thumbnail_url'] as String?,
      }).toList();
    } catch (e) {
      throw CacheException(message: '获取用户收藏内容失败: $e');
    }
  }
  
  @override
  Future<void> addToFavorites(String userId, String contentId) async {
    try {
      // 首先检查是否已存在相同记录
      final existingRecord = await _database.query(
        'user_favorites',
        where: 'user_id = ? AND content_id = ?',
        whereArgs: [userId, contentId],
      );
      
      if (existingRecord.isEmpty) {
        // 从内容表获取内容信息
        final contentInfo = await _database.query(
          'contents',
          where: 'id = ?',
          whereArgs: [contentId],
        );
        
        if (contentInfo.isNotEmpty) {
          // 添加新记录
          await _database.insert(
            'user_favorites',
            {
              'user_id': userId,
              'content_id': contentId,
              'title': contentInfo.first['title'],
              'added_date': DateTime.now().toIso8601String(),
              'content_type': contentInfo.first['content_type'],
              'thumbnail_url': contentInfo.first['thumbnail_url'],
            },
          );
        } else {
          // 如果内容信息不存在，则仅记录ID和时间
          await _database.insert(
            'user_favorites',
            {
              'user_id': userId,
              'content_id': contentId,
              'title': '未知内容',
              'added_date': DateTime.now().toIso8601String(),
              'content_type': 'unknown',
              'thumbnail_url': null,
            },
          );
        }
      }
    } catch (e) {
      throw CacheException(message: '添加收藏失败: $e');
    }
  }
  
  @override
  Future<void> removeFromFavorites(String userId, String contentId) async {
    try {
      await _database.delete(
        'user_favorites',
        where: 'user_id = ? AND content_id = ?',
        whereArgs: [userId, contentId],
      );
    } catch (e) {
      throw CacheException(message: '移除收藏失败: $e');
    }
  }
  
  @override
  Future<void> cacheUserFavorites(String userId, List<Map<String, dynamic>> favorites) async {
    try {
      // 开始事务
      await _database.transaction((txn) async {
        // 清除该用户的所有收藏记录
        await txn.delete(
          'user_favorites',
          where: 'user_id = ?',
          whereArgs: [userId],
        );
        
        // 插入新的收藏记录
        for (var item in favorites) {
          await txn.insert(
            'user_favorites',
            {
              'user_id': userId,
              'content_id': item['contentId'],
              'title': item['title'],
              'added_date': item['addedDate'],
              'content_type': item['contentType'],
              'thumbnail_url': item['thumbnailUrl'],
            },
          );
        }
      });
    } catch (e) {
      throw CacheException(message: '缓存用户收藏内容失败: $e');
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> getUserSocialShares(String userId, {int limit = 10, int offset = 0}) async {
    try {
      final results = await _database.query(
        'user_social_shares',
        where: 'user_id = ?',
        whereArgs: [userId],
        orderBy: 'share_date DESC',
        limit: limit,
        offset: offset,
      );
      
      return results.map((row) => {
        'id': row['id'] as String,
        'contentId': row['content_id'] as String,
        'title': row['title'] as String,
        'shareDate': row['share_date'] as String,
        'platform': row['platform'] as String,
        'shareText': row['share_text'] as String,
        'shareUrl': row['share_url'] as String,
        'thumbnailUrl': row['thumbnail_url'] as String?,
      }).toList();
    } catch (e) {
      throw CacheException(message: '获取用户社交分享失败: $e');
    }
  }
  
  @override
  Future<void> cacheUserSocialShares(String userId, List<Map<String, dynamic>> socialShares) async {
    try {
      // 开始事务
      await _database.transaction((txn) async {
        // 清除该用户的所有社交分享记录
        await txn.delete(
          'user_social_shares',
          where: 'user_id = ?',
          whereArgs: [userId],
        );
        
        // 插入新的社交分享记录
        for (var item in socialShares) {
          await txn.insert(
            'user_social_shares',
            {
              'id': item['id'],
              'user_id': userId,
              'content_id': item['contentId'],
              'title': item['title'],
              'share_date': item['shareDate'],
              'platform': item['platform'],
              'share_text': item['shareText'],
              'share_url': item['shareUrl'],
              'thumbnail_url': item['thumbnailUrl'],
            },
          );
        }
      });
    } catch (e) {
      throw CacheException(message: '缓存用户社交分享失败: $e');
    }
  }
  
  @override
  Future<void> cacheSocialShare(String userId, Map<String, dynamic> socialShare) async {
    try {
      // 检查记录是否已存在
      final existingRecord = await _database.query(
        'user_social_shares',
        where: 'id = ?',
        whereArgs: [socialShare['id']],
      );
      
      if (existingRecord.isNotEmpty) {
        // 更新已有记录
        await _database.update(
          'user_social_shares',
          {
            'content_id': socialShare['contentId'],
            'title': socialShare['title'],
            'share_date': socialShare['shareDate'],
            'platform': socialShare['platform'],
            'share_text': socialShare['shareText'],
            'share_url': socialShare['shareUrl'],
            'thumbnail_url': socialShare['thumbnailUrl'],
          },
          where: 'id = ?',
          whereArgs: [socialShare['id']],
        );
      } else {
        // 插入新记录
        await _database.insert(
          'user_social_shares',
          {
            'id': socialShare['id'],
            'user_id': userId,
            'content_id': socialShare['contentId'],
            'title': socialShare['title'],
            'share_date': socialShare['shareDate'],
            'platform': socialShare['platform'],
            'share_text': socialShare['shareText'],
            'share_url': socialShare['shareUrl'],
            'thumbnail_url': socialShare['thumbnailUrl'],
          },
        );
      }
    } catch (e) {
      throw CacheException(message: '缓存社交分享失败: $e');
    }
  }
} 