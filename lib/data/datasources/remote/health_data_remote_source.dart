import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:logger/logger.dart';

import '../../../core/error/exceptions.dart';
import '../../../domain/entities/health_data.dart';
import '../../models/health_data_model.dart';
import '../health_data_source.dart';

/// 健康数据远程数据源实现
/// 负责与服务器交互获取和保存健康数据
class HealthDataRemoteSource implements HealthDataSource {
  final Dio _dio;
  final Logger _logger;
  
  // API端点
  static const String _baseUrl = 'http://118.31.223.213/api';
  static const String _healthDataEndpoint = '/health-data';
  
  HealthDataRemoteSource({
    required Dio dio,
    required Logger logger,
  })  : _dio = dio,
        _logger = logger;
  
  @override
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
        'userId': userId,
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
      final response = await _dio.get(
        '$_baseUrl$_healthDataEndpoint',
        queryParameters: queryParams,
      );
      
      // 检查响应状态
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'];
        return data.map((item) => HealthDataModel.fromJson(item)).toList();
      } else {
        throw ServerException(
          message: '获取用户健康数据失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('获取用户健康数据失败: $e');
      throw ServerException(
        message: '获取用户健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('获取用户健康数据失败: $e');
      throw ServerException(
        message: '获取用户健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<HealthDataModel>> getHealthDataByType(
    String userId,
    HealthDataType type, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    try {
      // 构建查询参数
      final Map<String, dynamic> queryParams = {
        'userId': userId,
        'type': type.toString(),
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
      final response = await _dio.get(
        '$_baseUrl$_healthDataEndpoint/by-type',
        queryParameters: queryParams,
      );
      
      // 检查响应状态
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'];
        return data.map((item) => HealthDataModel.fromJson(item)).toList();
      } else {
        throw ServerException(
          message: '获取用户特定类型健康数据失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('获取用户特定类型健康数据失败: $e');
      throw ServerException(
        message: '获取用户特定类型健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('获取用户特定类型健康数据失败: $e');
      throw ServerException(
        message: '获取用户特定类型健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<HealthDataModel> getHealthDataById(String dataId) async {
    try {
      // 发送请求
      final response = await _dio.get(
        '$_baseUrl$_healthDataEndpoint/$dataId',
      );
      
      // 检查响应状态
      if (response.statusCode == 200) {
        return HealthDataModel.fromJson(response.data['data']);
      } else {
        throw ServerException(
          message: '获取健康数据详情失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('获取健康数据详情失败: $e');
      throw ServerException(
        message: '获取健康数据详情失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('获取健康数据详情失败: $e');
      throw ServerException(
        message: '获取健康数据详情失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<HealthDataModel> saveHealthData(HealthDataModel data) async {
    try {
      // 发送请求
      final response = await _dio.post(
        '$_baseUrl$_healthDataEndpoint',
        data: data.toJson(),
      );
      
      // 检查响应状态
      if (response.statusCode == 201 || response.statusCode == 200) {
        return HealthDataModel.fromJson(response.data['data']);
      } else {
        throw ServerException(
          message: '保存健康数据失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('保存健康数据失败: $e');
      throw ServerException(
        message: '保存健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('保存健康数据失败: $e');
      throw ServerException(
        message: '保存健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<HealthDataModel>> saveBatchHealthData(List<HealthDataModel> dataList) async {
    try {
      // 准备数据
      final List<Map<String, dynamic>> dataJson = dataList.map((data) => data.toJson()).toList();
      
      // 发送请求
      final response = await _dio.post(
        '$_baseUrl$_healthDataEndpoint/batch',
        data: {'data': dataJson},
      );
      
      // 检查响应状态
      if (response.statusCode == 201 || response.statusCode == 200) {
        final List<dynamic> responseData = response.data['data'];
        return responseData.map((item) => HealthDataModel.fromJson(item)).toList();
      } else {
        throw ServerException(
          message: '批量保存健康数据失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('批量保存健康数据失败: $e');
      throw ServerException(
        message: '批量保存健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('批量保存健康数据失败: $e');
      throw ServerException(
        message: '批量保存健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<HealthDataModel> updateHealthData(HealthDataModel data) async {
    try {
      // 发送请求
      final response = await _dio.put(
        '$_baseUrl$_healthDataEndpoint/${data.id}',
        data: data.toJson(),
      );
      
      // 检查响应状态
      if (response.statusCode == 200) {
        return HealthDataModel.fromJson(response.data['data']);
      } else {
        throw ServerException(
          message: '更新健康数据失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('更新健康数据失败: $e');
      throw ServerException(
        message: '更新健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('更新健康数据失败: $e');
      throw ServerException(
        message: '更新健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<void> deleteHealthData(String dataId) async {
    try {
      // 发送请求
      final response = await _dio.delete(
        '$_baseUrl$_healthDataEndpoint/$dataId',
      );
      
      // 检查响应状态
      if (response.statusCode != 200 && response.statusCode != 204) {
        throw ServerException(
          message: '删除健康数据失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('删除健康数据失败: $e');
      throw ServerException(
        message: '删除健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('删除健康数据失败: $e');
      throw ServerException(
        message: '删除健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<void> deleteBatchHealthData(List<String> dataIds) async {
    try {
      // 发送请求
      final response = await _dio.delete(
        '$_baseUrl$_healthDataEndpoint/batch',
        data: {'ids': dataIds},
      );
      
      // 检查响应状态
      if (response.statusCode != 200 && response.statusCode != 204) {
        throw ServerException(
          message: '批量删除健康数据失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('批量删除健康数据失败: $e');
      throw ServerException(
        message: '批量删除健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('批量删除健康数据失败: $e');
      throw ServerException(
        message: '批量删除健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<Map<HealthDataType, num>> getDailyHealthSummary(
    String userId,
    DateTime date,
  ) async {
    try {
      // 构建查询参数
      final Map<String, dynamic> queryParams = {
        'userId': userId,
        'date': date.toIso8601String().split('T')[0], // 只取日期部分
      };
      
      // 发送请求
      final response = await _dio.get(
        '$_baseUrl$_healthDataEndpoint/daily-summary',
        queryParameters: queryParams,
      );
      
      // 检查响应状态
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = response.data['data'];
        final Map<HealthDataType, num> result = {};
        
        // 转换响应数据
        data.forEach((key, value) {
          try {
            final type = HealthDataType.values.firstWhere(
              (t) => t.toString() == key,
            );
            result[type] = value;
          } catch (_) {
            // 忽略无法识别的类型
          }
        });
        
        return result;
      } else {
        throw ServerException(
          message: '获取每日健康数据汇总失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('获取每日健康数据汇总失败: $e');
      throw ServerException(
        message: '获取每日健康数据汇总失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('获取每日健康数据汇总失败: $e');
      throw ServerException(
        message: '获取每日健康数据汇总失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<Map<String, dynamic>> getHealthStatistics(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    String? groupBy,
  }) async {
    try {
      // 构建查询参数
      final Map<String, dynamic> queryParams = {
        'userId': userId,
        'type': type.toString(),
        'startDate': startDate.toIso8601String(),
        'endDate': endDate.toIso8601String(),
      };
      
      if (groupBy != null) {
        queryParams['groupBy'] = groupBy;
      }
      
      // 发送请求
      final response = await _dio.get(
        '$_baseUrl$_healthDataEndpoint/statistics',
        queryParameters: queryParams,
      );
      
      // 检查响应状态
      if (response.statusCode == 200) {
        return response.data['data'];
      } else {
        throw ServerException(
          message: '获取健康数据统计失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('获取健康数据统计失败: $e');
      throw ServerException(
        message: '获取健康数据统计失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('获取健康数据统计失败: $e');
      throw ServerException(
        message: '获取健康数据统计失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<HealthDataModel?> getLatestHealthData(
    String userId,
    HealthDataType type,
  ) async {
    try {
      // 构建查询参数
      final Map<String, dynamic> queryParams = {
        'userId': userId,
        'type': type.toString(),
      };
      
      // 发送请求
      final response = await _dio.get(
        '$_baseUrl$_healthDataEndpoint/latest',
        queryParameters: queryParams,
      );
      
      // 检查响应状态
      if (response.statusCode == 200) {
        if (response.data['data'] == null) {
          return null;
        }
        return HealthDataModel.fromJson(response.data['data']);
      } else {
        throw ServerException(
          message: '获取最新健康数据失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('获取最新健康数据失败: $e');
      throw ServerException(
        message: '获取最新健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('获取最新健康数据失败: $e');
      throw ServerException(
        message: '获取最新健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> getHealthTrend(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    required String interval,
  }) async {
    try {
      // 构建查询参数
      final Map<String, dynamic> queryParams = {
        'userId': userId,
        'type': type.toString(),
        'startDate': startDate.toIso8601String(),
        'endDate': endDate.toIso8601String(),
        'interval': interval,
      };
      
      // 发送请求
      final response = await _dio.get(
        '$_baseUrl$_healthDataEndpoint/trend',
        queryParameters: queryParams,
      );
      
      // 检查响应状态
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'];
        return data.map((item) => item as Map<String, dynamic>).toList();
      } else {
        throw ServerException(
          message: '获取健康数据趋势失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('获取健康数据趋势失败: $e');
      throw ServerException(
        message: '获取健康数据趋势失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('获取健康数据趋势失败: $e');
      throw ServerException(
        message: '获取健康数据趋势失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<List<HealthDataModel>> syncExternalHealthData(
    String userId,
    String source, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      // 构建查询参数
      final Map<String, dynamic> queryParams = {
        'userId': userId,
        'source': source,
      };
      
      if (startDate != null) {
        queryParams['startDate'] = startDate.toIso8601String();
      }
      
      if (endDate != null) {
        queryParams['endDate'] = endDate.toIso8601String();
      }
      
      // 发送请求
      final response = await _dio.post(
        '$_baseUrl$_healthDataEndpoint/sync',
        queryParameters: queryParams,
      );
      
      // 检查响应状态
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'];
        return data.map((item) => HealthDataModel.fromJson(item)).toList();
      } else {
        throw ServerException(
          message: '同步外部健康数据失败: ${response.statusCode}',
          statusCode: response.statusCode ?? 500,
        );
      }
    } on DioException catch (e) {
      _logger.e('同步外部健康数据失败: $e');
      throw ServerException(
        message: '同步外部健康数据失败: ${e.message}',
        statusCode: e.response?.statusCode ?? 500,
      );
    } catch (e) {
      _logger.e('同步外部健康数据失败: $e');
      throw ServerException(
        message: '同步外部健康数据失败: $e',
        statusCode: 500,
      );
    }
  }
} 