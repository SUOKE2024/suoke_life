import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/utils/logger.dart';

/// 网络连接状态
enum NetworkStatus {
  /// 在线
  online,

  /// 离线
  offline,

  /// 通过移动网络连接
  cellular,

  /// 通过WiFi连接
  wifi,

  /// 通过以太网连接
  ethernet,

  /// 未知状态
  unknown,
}

/// 网络服务
///
/// 管理网络连接状态和网络请求功能
class NetworkService {
  static const String _tag = 'NetworkService';

  /// 连接状态流控制器
  final _networkStatusController = StreamController<NetworkStatus>.broadcast();

  /// 连接监听器
  StreamSubscription<ConnectivityResult>? _connectivitySubscription;

  /// Dio HTTP客户端
  final Dio _dio;

  /// 当前网络状态
  NetworkStatus _currentStatus = NetworkStatus.unknown;

  /// 连接测试定时器
  Timer? _connectionTestTimer;

  /// 构造函数
  NetworkService(this._dio) {
    _initConnectivityListener();
  }

  /// 初始化连接监听
  Future<void> _initConnectivityListener() async {
    try {
      final connectivity = Connectivity();
      final initialResult = await connectivity.checkConnectivity();
      _updateNetworkStatus(initialResult);

      _connectivitySubscription = connectivity.onConnectivityChanged.listen((result) {
        _updateNetworkStatus(result);
      });

      // 每30秒进行一次连接测试
      _connectionTestTimer = Timer.periodic(const Duration(seconds: 30), (_) {
        _testConnection();
      });
    } catch (e) {
      Logger.e(_tag, 'Failed to initialize connectivity listener: $e');
      _currentStatus = NetworkStatus.unknown;
      _networkStatusController.add(_currentStatus);
    }
  }

  /// 获取网络状态流
  Stream<NetworkStatus> get networkStatusStream => _networkStatusController.stream;

  /// 获取当前网络状态
  NetworkStatus get currentStatus => _currentStatus;

  /// 更新网络状态
  void _updateNetworkStatus(ConnectivityResult result) {
    switch (result) {
      case ConnectivityResult.mobile:
        _currentStatus = NetworkStatus.cellular;
        break;
      case ConnectivityResult.wifi:
        _currentStatus = NetworkStatus.wifi;
        break;
      case ConnectivityResult.ethernet:
        _currentStatus = NetworkStatus.ethernet;
        break;
      default:
        _currentStatus = NetworkStatus.offline;
    }

    // 如果不是离线状态，测试实际连接
    if (_currentStatus != NetworkStatus.offline) {
      _testConnection();
    } else {
      _networkStatusController.add(_currentStatus);
    }
  }

  /// 测试实际连接
  Future<void> _testConnection() async {
    try {
      final response = await _dio.get(
        ApiConstants.connectionTestUrl,
        options: Options(
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );

      if (response.statusCode == 200) {
        if (_currentStatus == NetworkStatus.offline) {
          _currentStatus = NetworkStatus.online;
        }
      } else {
        _currentStatus = NetworkStatus.offline;
      }
    } catch (e) {
      _currentStatus = NetworkStatus.offline;
    }

    _networkStatusController.add(_currentStatus);
  }

  /// 发送HTTP GET请求
  Future<dynamic> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return _handleResponse(response);
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  /// 发送HTTP POST请求
  Future<dynamic> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return _handleResponse(response);
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  /// 发送HTTP PUT请求
  Future<dynamic> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return _handleResponse(response);
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  /// 发送HTTP DELETE请求
  Future<dynamic> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return _handleResponse(response);
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  /// 处理响应数据
  dynamic _handleResponse(Response response) {
    if (response.statusCode! >= 200 && response.statusCode! < 300) {
      return response.data;
    } else {
      throw Exception('API错误: 状态码 ${response.statusCode}');
    }
  }

  /// 处理Dio异常
  Exception _handleDioException(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
        return Exception('连接超时，请检查网络连接');
      case DioExceptionType.sendTimeout:
        return Exception('发送请求超时，请检查网络连接');
      case DioExceptionType.receiveTimeout:
        return Exception('接收响应超时，请检查网络连接');
      case DioExceptionType.badCertificate:
        return Exception('证书验证失败');
      case DioExceptionType.badResponse:
        if (e.response != null) {
          final statusCode = e.response!.statusCode;
          final data = e.response!.data;
          String message = '未知错误';
          
          if (data is Map && data.containsKey('message')) {
            message = data['message'] as String;
          } else if (data is String) {
            message = data;
          }
          
          return Exception('API错误 ($statusCode): $message');
        }
        return Exception('API错误: 无效的响应');
      case DioExceptionType.cancel:
        return Exception('请求被取消');
      case DioExceptionType.connectionError:
        return Exception('网络连接错误，请检查网络连接');
      case DioExceptionType.unknown:
      default:
        if (e.error is SocketException) {
          return Exception('网络连接失败，请检查网络连接');
        }
        return Exception('网络请求失败: ${e.message}');
    }
  }

  /// 销毁服务
  void dispose() {
    _connectivitySubscription?.cancel();
    _connectionTestTimer?.cancel();
    _networkStatusController.close();
  }
}

/// 网络服务Provider
final networkServiceProvider = Provider<NetworkService>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: ApiConstants.apiBaseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    headers: {'Content-Type': 'application/json'},
  ));
  
  final service = NetworkService(dio);
  
  ref.onDispose(() {
    service.dispose();
  });
  
  return service;
});

/// 网络状态Provider
final networkStatusProvider = StreamProvider<NetworkStatus>((ref) {
  final networkService = ref.watch(networkServiceProvider);
  return networkService.networkStatusStream;
});

/// 是否在线Provider
final isOnlineProvider = Provider<bool>((ref) {
  final networkStatusAsyncValue = ref.watch(networkStatusProvider);
  
  return networkStatusAsyncValue.when(
    data: (status) => status != NetworkStatus.offline,
    loading: () => false, // 加载中默认为离线
    error: (_, __) => false, // 错误时默认为离线
  );
});
