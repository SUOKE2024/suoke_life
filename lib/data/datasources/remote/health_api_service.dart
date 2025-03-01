import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../../../core/error/exceptions.dart';
import '../../models/health_data_model.dart';

/// API配置常量
class ApiEndpoints {
  static const String baseUrl = 'http://118.31.223.213/api';
  static const String healthData = '/health-data';
  static const String users = '/users';
  static const String knowledge = '/knowledge';
}

/// 健康数据API服务
/// 负责与服务器交互获取和保存健康数据
class HealthApiService {
  final ApiClient _apiClient;
  
  /// 构造函数
  HealthApiService(this._apiClient);
  
  /// 获取用户健康数据
  Future<List<HealthDataModel>> getUserHealthData(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    try {
      // 构建查询参数
      final Map<String, dynamic> queryParams = {
        'limit': limit,
        'offset': offset,
      };
      
      if (startDate != null) {
        queryParams['startDate'] = startDate.toIso8601String();
      }
      
      if (endDate != null) {
        queryParams['endDate'] = endDate.toIso8601String();
      }
      
      // 发送请求
      final response = await _apiClient.get(
        '${ApiEndpoints.healthData}/$userId',
        queryParameters: queryParams,
      );
      
      // 解析响应
      final data = response.data['data'] as List<dynamic>;
      return data.map((item) => HealthDataModel.fromJson(item)).toList();
    } on DioException catch (e) {
      throw ServerException(
        message: '获取健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      throw ServerException(
        message: '获取健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  /// 保存健康数据
  Future<HealthDataModel> saveHealthData(HealthDataModel data) async {
    try {
      final response = await _apiClient.post(
        ApiEndpoints.healthData,
        data: data.toJson(),
      );
      
      return HealthDataModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw ServerException(
        message: '保存健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      throw ServerException(
        message: '保存健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  /// 批量保存健康数据
  Future<List<HealthDataModel>> saveBatchHealthData(List<HealthDataModel> dataList) async {
    try {
      final List<Map<String, dynamic>> jsonList = dataList.map((e) => e.toJson()).toList();
      
      final response = await _apiClient.post(
        '${ApiEndpoints.healthData}/batch',
        data: {'data': jsonList},
      );
      
      final List<dynamic> responseData = response.data['data'];
      return responseData.map((item) => HealthDataModel.fromJson(item)).toList();
    } on DioException catch (e) {
      throw ServerException(
        message: '批量保存健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      throw ServerException(
        message: '批量保存健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  /// 更新健康数据
  Future<HealthDataModel> updateHealthData(HealthDataModel data) async {
    try {
      final response = await _apiClient.put(
        '${ApiEndpoints.healthData}/${data.id}',
        data: data.toJson(),
      );
      
      return HealthDataModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw ServerException(
        message: '更新健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      throw ServerException(
        message: '更新健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  /// 删除健康数据
  Future<void> deleteHealthData(String dataId) async {
    try {
      await _apiClient.delete(
        '${ApiEndpoints.healthData}/$dataId',
      );
    } on DioException catch (e) {
      throw ServerException(
        message: '删除健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      throw ServerException(
        message: '删除健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  /// 批量删除健康数据
  Future<void> deleteBatchHealthData(List<String> dataIds) async {
    try {
      await _apiClient.delete(
        '${ApiEndpoints.healthData}/batch',
        data: {'ids': dataIds},
      );
    } on DioException catch (e) {
      throw ServerException(
        message: '批量删除健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      throw ServerException(
        message: '批量删除健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  /// 获取健康数据统计信息
  Future<Map<String, dynamic>> getHealthStatistics(
    String userId,
    String type, {
    required DateTime startDate,
    required DateTime endDate,
    String? groupBy,
  }) async {
    try {
      final Map<String, dynamic> queryParams = {
        'type': type,
        'startDate': startDate.toIso8601String(),
        'endDate': endDate.toIso8601String(),
      };
      
      if (groupBy != null) {
        queryParams['groupBy'] = groupBy;
      }
      
      final response = await _apiClient.get(
        '${ApiEndpoints.healthData}/$userId/statistics',
        queryParameters: queryParams,
      );
      
      return response.data['data'];
    } on DioException catch (e) {
      throw ServerException(
        message: '获取健康数据统计失败: ${e.message}',
        statusCode: e.response?.statusCode,
      );
    } catch (e) {
      throw ServerException(
        message: '获取健康数据统计失败: $e',
        statusCode: 500,
      );
    }
  }
}

/// 健康API服务提供者
final healthApiServiceProvider = Provider<HealthApiService>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return HealthApiService(apiClient);
});