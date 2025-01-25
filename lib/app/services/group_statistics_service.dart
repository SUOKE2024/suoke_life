import 'package:get/get.dart';
import '../core/network/api_client.dart';
import '../data/models/active_member.dart';

class GroupStatisticsService extends GetxService {
  final ApiClient _apiClient;
  
  GroupStatisticsService({required ApiClient apiClient}) : _apiClient = apiClient;

  // 获取群聊概览数据
  Future<Map<String, dynamic>> getOverview(String groupId) async {
    try {
      final response = await _apiClient.get('/groups/$groupId/statistics/overview');
      return {
        'totalMessages': response['totalMessages'],
        'todayMessages': response['todayMessages'],
        'activeMembers': response['activeMembers'],
      };
    } catch (e) {
      rethrow;
    }
  }

  // 获取活跃成员排行
  Future<List<ActiveMember>> getTopMembers(String groupId, {
    String timeRange = 'week',
    int limit = 10,
  }) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/statistics/members',
        queryParameters: {
          'timeRange': timeRange,
          'limit': limit,
        },
      );
      return (response['members'] as List)
          .map((json) => ActiveMember.fromJson(json))
          .toList();
    } catch (e) {
      rethrow;
    }
  }

  // 获取消息趋势数据
  Future<List<Map<String, dynamic>>> getMessageTrend(String groupId, {
    String timeRange = 'week',
  }) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/statistics/trend',
        queryParameters: {'timeRange': timeRange},
      );
      return List<Map<String, dynamic>>.from(response['trend']);
    } catch (e) {
      rethrow;
    }
  }

  // 获取消息类型分布
  Future<Map<String, int>> getMessageTypes(String groupId, {
    String timeRange = 'week',
  }) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/statistics/types',
        queryParameters: {'timeRange': timeRange},
      );
      return Map<String, int>.from(response['types']);
    } catch (e) {
      rethrow;
    }
  }

  // 获取活跃时段分析
  Future<Map<String, int>> getActiveTime(String groupId, {
    String timeRange = 'week',
  }) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/statistics/active-time',
        queryParameters: {'timeRange': timeRange},
      );
      return Map<String, int>.from(response['activeTime']);
    } catch (e) {
      rethrow;
    }
  }

  // 获取成员互动分析
  Future<List<Map<String, dynamic>>> getMemberInteractions(String groupId, {
    String timeRange = 'week',
    int limit = 10,
  }) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/statistics/interactions',
        queryParameters: {
          'timeRange': timeRange,
          'limit': limit,
        },
      );
      return List<Map<String, dynamic>>.from(response['interactions']);
    } catch (e) {
      rethrow;
    }
  }

  // 获取群聊热词分析
  Future<List<Map<String, dynamic>>> getHotWords(String groupId, {
    String timeRange = 'week',
    int limit = 20,
  }) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/statistics/hot-words',
        queryParameters: {
          'timeRange': timeRange,
          'limit': limit,
        },
      );
      return List<Map<String, dynamic>>.from(response['hotWords']);
    } catch (e) {
      rethrow;
    }
  }

  // 导出统计数据
  Future<String> exportStatistics(String groupId, {
    String timeRange = 'week',
    String format = 'excel',
  }) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/statistics/export',
        queryParameters: {
          'timeRange': timeRange,
          'format': format,
        },
      );
      return response['downloadUrl'];
    } catch (e) {
      rethrow;
    }
  }

  // 导出分析数据
  Future<String> exportAnalysis(String groupId, {
    String timeRange = 'week',
    String format = 'excel',
  }) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/statistics/export',
        queryParameters: {
          'timeRange': timeRange,
          'format': format,
        },
      );
      return response['downloadUrl'];
    } catch (e) {
      rethrow;
    }
  }
} 