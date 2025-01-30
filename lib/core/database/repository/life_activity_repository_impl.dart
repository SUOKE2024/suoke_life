import 'dart:convert';
import 'package:logger/logger.dart';

import '../local/dao/life_activity_dao.dart';
import '../models/life_activity_data.dart';
import 'life_activity_repository.dart';

/// 生活活动数据仓库实现类
class LifeActivityRepositoryImpl implements LifeActivityRepository {
  final LifeActivityDao _dao;
  final Logger _logger = Logger();

  LifeActivityRepositoryImpl(this._dao);

  @override
  Future<void> recordActivity(LifeActivityData activity) async {
    try {
      await _dao.insert(activity);
      _logger.i('Activity recorded successfully: ${activity.type}');
    } catch (e) {
      _logger.e('Error recording activity: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeActivityData>> getActivityHistory(String userId, {
    String? type,
    int? startTime,
    int? endTime,
    String? location,
  }) async {
    try {
      if (type != null && startTime != null && endTime != null) {
        return await _dao.findByUserIdTypeAndTimeRange(userId, type, startTime, endTime);
      } else if (type != null) {
        return await _dao.findByUserIdAndType(userId, type);
      } else if (location != null) {
        return await _dao.findByLocation(location);
      } else if (startTime != null && endTime != null) {
        return await _dao.findByTimeRange(startTime, endTime);
      } else {
        return await _dao.findByUserId(userId);
      }
    } catch (e) {
      _logger.e('Error getting activity history: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, dynamic>> getActivityStatistics(String userId, {
    String? type,
    int? startTime,
    int? endTime,
  }) async {
    try {
      final Map<String, dynamic> statistics = {};
      final types = type != null ? [type] : await _dao.getUserActivityTypes(userId);

      for (final activityType in types) {
        final start = startTime ?? DateTime.now().subtract(const Duration(days: 30)).millisecondsSinceEpoch;
        final end = endTime ?? DateTime.now().millisecondsSinceEpoch;

        final totalDuration = await _dao.getTotalDuration(userId, activityType, start, end);
        final totalValue = await _dao.getTotalValue(userId, activityType, start, end);
        final frequency = await _dao.getActivityFrequency(userId, activityType, start, end);

        statistics[activityType] = {
          'totalDuration': totalDuration,
          'totalValue': totalValue,
          'frequency': frequency,
          'averagePerDay': frequency.isEmpty ? 0 : frequency.values.reduce((a, b) => a + b) / frequency.length,
        };
      }

      return statistics;
    } catch (e) {
      _logger.e('Error getting activity statistics: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, List<dynamic>>> getActivityTrends(String userId, {
    String? type,
    int? startTime,
    int? endTime,
  }) async {
    try {
      final Map<String, List<dynamic>> trends = {};
      final types = type != null ? [type] : await _dao.getUserActivityTypes(userId);
      final start = startTime ?? DateTime.now().subtract(const Duration(days: 30)).millisecondsSinceEpoch;
      final end = endTime ?? DateTime.now().millisecondsSinceEpoch;

      for (final activityType in types) {
        final activities = await _dao.findByUserIdTypeAndTimeRange(userId, activityType, start, end);
        final List<Map<String, dynamic>> trend = [];

        for (final activity in activities) {
          trend.add({
            'time': activity.time,
            'value': activity.value,
            'duration': activity.duration,
          });
        }

        trends[activityType] = trend;
      }

      return trends;
    } catch (e) {
      _logger.e('Error getting activity trends: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, String>> getActivityRecommendations(String userId) async {
    try {
      final Map<String, String> recommendations = {};
      final types = await _dao.getUserActivityTypes(userId);
      final now = DateTime.now();
      final lastWeek = now.subtract(const Duration(days: 7));

      for (final type in types) {
        final activities = await _dao.findByUserIdTypeAndTimeRange(
          userId,
          type,
          lastWeek.millisecondsSinceEpoch,
          now.millisecondsSinceEpoch,
        );

        if (activities.isEmpty) {
          recommendations[type] = '建议开始进行$type活动，保持规律的生活习惯';
        } else {
          final totalDuration = activities.fold<int>(0, (sum, activity) => sum + (activity.duration ?? 0));
          final averageDuration = totalDuration ~/ 7;

          if (averageDuration < 30 * 60) { // 小于30分钟
            recommendations[type] = '建议增加$type活动的时长，每天至少进行30分钟';
          } else if (averageDuration > 120 * 60) { // 超过2小时
            recommendations[type] = '您的$type活动时间较长，注意适度，避免过度疲劳';
          } else {
            recommendations[type] = '您的$type活动频率和时长都很合理，请继续保持';
          }
        }
      }

      return recommendations;
    } catch (e) {
      _logger.e('Error getting activity recommendations: $e');
      rethrow;
    }
  }

  @override
  Future<String> exportActivityData(String userId, {
    String? type,
    int? startTime,
    int? endTime,
  }) async {
    try {
      final activities = await getActivityHistory(
        userId,
        type: type,
        startTime: startTime,
        endTime: endTime,
      );

      final exportData = {
        'userId': userId,
        'exportTime': DateTime.now().toIso8601String(),
        'activities': activities.map((activity) => activity.toMap()).toList(),
      };

      return jsonEncode(exportData);
    } catch (e) {
      _logger.e('Error exporting activity data: $e');
      rethrow;
    }
  }

  @override
  Future<void> importActivityData(String userId, String data) async {
    try {
      final Map<String, dynamic> importData = jsonDecode(data);
      final List<dynamic> activitiesList = importData['activities'] as List<dynamic>;

      final activities = activitiesList
          .map((map) => LifeActivityData.fromMap(map as Map<String, dynamic>))
          .toList();

      await _dao.saveAll(activities);
      _logger.i('Successfully imported ${activities.length} activities');
    } catch (e) {
      _logger.e('Error importing activity data: $e');
      rethrow;
    }
  }

  @override
  Future<void> syncToCloud(String userId) async {
    try {
      // TODO: 实现云端同步功能
      _logger.i('Syncing data to cloud for user: $userId');
    } catch (e) {
      _logger.e('Error syncing data to cloud: $e');
      rethrow;
    }
  }

  @override
  Future<void> syncFromCloud(String userId) async {
    try {
      // TODO: 实现从云端同步功能
      _logger.i('Syncing data from cloud for user: $userId');
    } catch (e) {
      _logger.e('Error syncing data from cloud: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteUserActivities(String userId, {String? type}) async {
    try {
      if (type != null) {
        await _dao.deleteByType(userId, type);
        _logger.i('Deleted activities of type $type for user $userId');
      } else {
        await _dao.deleteByUserId(userId);
        _logger.i('Deleted all activities for user $userId');
      }
    } catch (e) {
      _logger.e('Error deleting user activities: $e');
      rethrow;
    }
  }

  @override
  Future<void> clearAllActivities() async {
    try {
      await _dao.clear();
      _logger.i('Cleared all activity data');
    } catch (e) {
      _logger.e('Error clearing all activities: $e');
      rethrow;
    }
  }

  @override
  Future<void> delete(String id) async {
    try {
      await _dao.delete(id);
    } catch (e) {
      _logger.e('Error deleting activity: $e');
      rethrow;
    }
  }

  @override
  Future<LifeActivityData?> get(String id) async {
    try {
      return await _dao.get(id);
    } catch (e) {
      _logger.e('Error getting activity: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeActivityData>> getAll() async {
    try {
      return await _dao.getAll();
    } catch (e) {
      _logger.e('Error getting all activities: $e');
      rethrow;
    }
  }

  @override
  Future<void> insert(LifeActivityData entity) async {
    try {
      await _dao.insert(entity);
    } catch (e) {
      _logger.e('Error inserting activity: $e');
      rethrow;
    }
  }

  @override
  Future<void> update(LifeActivityData entity) async {
    try {
      await _dao.update(entity);
    } catch (e) {
      _logger.e('Error updating activity: $e');
      rethrow;
    }
  }
} 