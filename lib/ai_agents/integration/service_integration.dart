import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/security_privacy_framework.dart';

/// 服务类型
enum ServiceType {
  /// 医疗服务
  medical,
  
  /// 健康设备
  healthDevice,
  
  /// 知识库
  knowledgeBase,
  
  /// 农产品服务
  agriculture,
  
  /// 药食同源服务
  medicinalFood,
  
  /// 其他类型
  other,
}

/// 服务状态
enum ServiceStatus {
  /// 可用
  available,
  
  /// 不可用
  unavailable,
  
  /// 受限（需要额外授权）
  limited,
  
  /// 过期
  expired,
  
  /// 维护中
  maintenance,
}

/// 服务请求结果
class ServiceResponse<T> {
  /// 是否成功
  final bool success;
  
  /// 结果数据
  final T? data;
  
  /// 错误信息
  final String? error;
  
  /// 响应代码
  final int? statusCode;
  
  /// 元数据
  final Map<String, dynamic>? metadata;
  
  const ServiceResponse({
    required this.success,
    this.data,
    this.error,
    this.statusCode,
    this.metadata,
  });
  
  /// 创建成功的响应
  factory ServiceResponse.success(T data, {
    int? statusCode,
    Map<String, dynamic>? metadata,
  }) {
    return ServiceResponse<T>(
      success: true,
      data: data,
      statusCode: statusCode,
      metadata: metadata,
    );
  }
  
  /// 创建失败的响应
  factory ServiceResponse.error(String error, {
    int? statusCode,
    Map<String, dynamic>? metadata,
  }) {
    return ServiceResponse<T>(
      success: false,
      error: error,
      statusCode: statusCode,
      metadata: metadata,
    );
  }
}

/// 服务集成配置
class ServiceConfig {
  /// 服务ID
  final String id;
  
  /// 服务名称
  final String name;
  
  /// 服务类型
  final ServiceType type;
  
  /// 基础URL
  final String baseUrl;
  
  /// API密钥（如果需要）
  final String? apiKey;
  
  /// 认证类型
  final String? authType;
  
  /// 认证令牌（如果需要）
  final String? authToken;
  
  /// 超时设置（毫秒）
  final int timeout;
  
  /// 重试次数
  final int retryCount;
  
  /// 自定义头部
  final Map<String, String>? headers;
  
  /// 安全级别
  final PrivacyLevel privacyLevel;
  
  /// 是否需要用户明确同意
  final bool requiresUserConsent;
  
  const ServiceConfig({
    required this.id,
    required this.name,
    required this.type,
    required this.baseUrl,
    this.apiKey,
    this.authType,
    this.authToken,
    this.timeout = 10000,
    this.retryCount = 3,
    this.headers,
    this.privacyLevel = PrivacyLevel.personal,
    this.requiresUserConsent = true,
  });
}

/// 服务集成接口
abstract class ServiceIntegration {
  /// 服务配置
  ServiceConfig get config;
  
  /// 服务当前状态
  ServiceStatus get status;
  
  /// 初始化服务
  Future<void> initialize();
  
  /// 关闭服务
  Future<void> shutdown();
  
  /// 发送请求
  Future<ServiceResponse<T>> sendRequest<T>({
    required String endpoint,
    required String method,
    Map<String, dynamic>? queryParams,
    dynamic body,
    Map<String, String>? headers,
    String? userId,
  });
  
  /// 获取服务状态
  Future<ServiceStatus> checkStatus();
  
  /// 更新服务配置
  Future<void> updateConfig(ServiceConfig newConfig);
  
  /// 刷新认证令牌
  Future<String?> refreshToken();
}

/// 服务集成注册表
abstract class ServiceIntegrationRegistry {
  /// 注册服务
  Future<void> registerService(ServiceIntegration service);
  
  /// 注销服务
  Future<void> unregisterService(String serviceId);
  
  /// 获取服务
  ServiceIntegration? getService(String serviceId);
  
  /// 获取指定类型的所有服务
  List<ServiceIntegration> getServicesByType(ServiceType type);
  
  /// 获取所有服务
  List<ServiceIntegration> getAllServices();
  
  /// 监听服务状态变化
  Stream<MapEntry<String, ServiceStatus>> get serviceStatusStream;
}

/// 默认服务集成基类
abstract class BaseServiceIntegration implements ServiceIntegration {
  final ServiceConfig _config;
  ServiceStatus _status = ServiceStatus.unavailable;
  final Dio _dio = Dio();
  final SecurityPrivacyFramework _securityFramework;
  
  BaseServiceIntegration(this._config, this._securityFramework) {
    _dio.options.baseUrl = _config.baseUrl;
    _dio.options.connectTimeout = Duration(milliseconds: _config.timeout);
    
    if (_config.headers != null) {
      _dio.options.headers.addAll(_config.headers!);
    }
    
    if (_config.apiKey != null) {
      _dio.options.headers['X-API-Key'] = _config.apiKey;
    }
  }
  
  @override
  ServiceConfig get config => _config;
  
  @override
  ServiceStatus get status => _status;
  
  @override
  Future<void> initialize() async {
    _status = await checkStatus();
  }
  
  @override
  Future<void> shutdown() async {
    _status = ServiceStatus.unavailable;
  }
  
  @override
  Future<ServiceResponse<T>> sendRequest<T>({
    required String endpoint,
    required String method,
    Map<String, dynamic>? queryParams,
    dynamic body,
    Map<String, String>? headers,
    String? userId,
  }) async {
    if (_status != ServiceStatus.available && _status != ServiceStatus.limited) {
      return ServiceResponse.error('Service is not available');
    }
    
    // 如果需要用户同意，则进行权限检查
    if (_config.requiresUserConsent && userId != null) {
      final hasPermission = await _securityFramework.checkPermission(
        userId,
        SecurityOperation.read,
        _config.type.toString(),
        _config.privacyLevel,
      );
      
      if (!hasPermission) {
        return ServiceResponse.error('User does not have permission to access this service');
      }
    }
    
    // 构建请求选项
    final options = Options(
      method: method,
      headers: headers,
    );
    
    if (_config.authToken != null) {
      options.headers ??= {};
      options.headers!['Authorization'] = '${_config.authType ?? 'Bearer'} ${_config.authToken}';
    }
    
    try {
      Response response;
      
      switch (method.toUpperCase()) {
        case 'GET':
          response = await _dio.get(
            endpoint,
            queryParameters: queryParams,
            options: options,
          );
          break;
        case 'POST':
          response = await _dio.post(
            endpoint,
            data: body,
            queryParameters: queryParams,
            options: options,
          );
          break;
        case 'PUT':
          response = await _dio.put(
            endpoint,
            data: body,
            queryParameters: queryParams,
            options: options,
          );
          break;
        case 'DELETE':
          response = await _dio.delete(
            endpoint,
            data: body,
            queryParameters: queryParams,
            options: options,
          );
          break;
        default:
          return ServiceResponse.error('Unsupported method: $method');
      }
      
      // 记录审计事件
      if (userId != null) {
        await _securityFramework.logAuditEvent(
          SecurityAuditEvent(
            id: 'service_request_${DateTime.now().millisecondsSinceEpoch}',
            operation: SecurityOperation.read,
            dataType: _config.type.toString(),
            userId: userId,
            success: true,
          ),
        );
      }
      
      return ServiceResponse.success(
        response.data as T,
        statusCode: response.statusCode,
        metadata: {
          'headers': response.headers.map,
          'request_time': DateTime.now().toIso8601String(),
        },
      );
    } on DioException catch (e) {
      // 记录失败的审计事件
      if (userId != null) {
        await _securityFramework.logAuditEvent(
          SecurityAuditEvent(
            id: 'service_request_${DateTime.now().millisecondsSinceEpoch}',
            operation: SecurityOperation.read,
            dataType: _config.type.toString(),
            userId: userId,
            success: false,
            failureReason: e.toString(),
          ),
        );
      }
      
      return ServiceResponse.error(
        'API error: ${e.message}',
        statusCode: e.response?.statusCode,
        metadata: {
          'error_type': e.type.toString(),
          'request_time': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      // 记录失败的审计事件
      if (userId != null) {
        await _securityFramework.logAuditEvent(
          SecurityAuditEvent(
            id: 'service_request_${DateTime.now().millisecondsSinceEpoch}',
            operation: SecurityOperation.read,
            dataType: _config.type.toString(),
            userId: userId,
            success: false,
            failureReason: e.toString(),
          ),
        );
      }
      
      return ServiceResponse.error(
        'Unexpected error: $e',
        metadata: {
          'request_time': DateTime.now().toIso8601String(),
        },
      );
    }
  }
  
  @override
  Future<void> updateConfig(ServiceConfig newConfig) async {
    // 更新配置时需要重新初始化
    await shutdown();
    
    // 更新Dio客户端配置
    _dio.options.baseUrl = newConfig.baseUrl;
    _dio.options.connectTimeout = Duration(milliseconds: newConfig.timeout);
    
    // 清除旧的头部
    _dio.options.headers.clear();
    
    // 添加新的头部
    if (newConfig.headers != null) {
      _dio.options.headers.addAll(newConfig.headers!);
    }
    
    if (newConfig.apiKey != null) {
      _dio.options.headers['X-API-Key'] = newConfig.apiKey;
    }
    
    // 初始化服务
    await initialize();
  }
}

/// 默认服务集成注册表实现
class DefaultServiceIntegrationRegistry implements ServiceIntegrationRegistry {
  final Map<String, ServiceIntegration> _services = {};
  final StreamController<MapEntry<String, ServiceStatus>> _statusController = StreamController.broadcast();
  
  // 单例实现
  static final DefaultServiceIntegrationRegistry _instance = DefaultServiceIntegrationRegistry._internal();
  
  factory DefaultServiceIntegrationRegistry() => _instance;
  
  DefaultServiceIntegrationRegistry._internal();
  
  @override
  Future<void> registerService(ServiceIntegration service) async {
    _services[service.config.id] = service;
    
    // 初始化服务
    await service.initialize();
    
    // 发送状态更新
    _statusController.add(MapEntry(service.config.id, service.status));
  }
  
  @override
  Future<void> unregisterService(String serviceId) async {
    final service = _services.remove(serviceId);
    if (service != null) {
      await service.shutdown();
      
      // 发送状态更新
      _statusController.add(MapEntry(serviceId, ServiceStatus.unavailable));
    }
  }
  
  @override
  ServiceIntegration? getService(String serviceId) {
    return _services[serviceId];
  }
  
  @override
  List<ServiceIntegration> getServicesByType(ServiceType type) {
    return _services.values.where((service) => service.config.type == type).toList();
  }
  
  @override
  List<ServiceIntegration> getAllServices() {
    return _services.values.toList();
  }
  
  @override
  Stream<MapEntry<String, ServiceStatus>> get serviceStatusStream => _statusController.stream;
  
  /// 监控服务状态
  void startStatusMonitoring({Duration interval = const Duration(minutes: 5)}) {
    Timer.periodic(interval, (_) async {
      for (final service in _services.values) {
        final currentStatus = service.status;
        final newStatus = await service.checkStatus();
        
        if (currentStatus != newStatus) {
          _statusController.add(MapEntry(service.config.id, newStatus));
        }
      }
    });
  }
} 