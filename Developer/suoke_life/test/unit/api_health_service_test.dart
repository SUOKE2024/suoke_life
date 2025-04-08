import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

import 'api_health_service_test.mocks.dart';

// 创建一个简单的ApiHealthService和ApiHealthStatus模拟
enum ApiHealthStatus {
  unchecked,
  healthy,
  unhealthy,
  checking
}

class ApiHealthService {
  final Dio _dio;
  ApiHealthStatus _apiGatewayStatus = ApiHealthStatus.unchecked;
  ApiHealthStatus _authServiceStatus = ApiHealthStatus.unchecked;
  ApiHealthStatus _userServiceStatus = ApiHealthStatus.unchecked;
  
  ApiHealthService(this._dio);
  
  ApiHealthStatus get apiGatewayStatus => _apiGatewayStatus;
  ApiHealthStatus get authServiceStatus => _authServiceStatus;
  ApiHealthStatus get userServiceStatus => _userServiceStatus;
  
  Future<bool> checkApiGatewayHealth() async {
    _apiGatewayStatus = ApiHealthStatus.checking;
    try {
      final response = await _dio.get('/api/health');
      if (response.statusCode == 200) {
        _apiGatewayStatus = ApiHealthStatus.healthy;
        return true;
      } else {
        _apiGatewayStatus = ApiHealthStatus.unhealthy;
        return false;
      }
    } catch (e) {
      _apiGatewayStatus = ApiHealthStatus.unhealthy;
      return false;
    }
  }
  
  Future<bool> checkAuthServiceHealth() async {
    _authServiceStatus = ApiHealthStatus.checking;
    try {
      final response = await _dio.get('/auth/health');
      if (response.statusCode == 200) {
        _authServiceStatus = ApiHealthStatus.healthy;
        return true;
      } else {
        _authServiceStatus = ApiHealthStatus.unhealthy;
        return false;
      }
    } catch (e) {
      _authServiceStatus = ApiHealthStatus.unhealthy;
      return false;
    }
  }
  
  Future<bool> checkUserServiceHealth() async {
    _userServiceStatus = ApiHealthStatus.checking;
    try {
      final response = await _dio.get('/user/health');
      if (response.statusCode == 200) {
        _userServiceStatus = ApiHealthStatus.healthy;
        return true;
      } else {
        _userServiceStatus = ApiHealthStatus.unhealthy;
        return false;
      }
    } catch (e) {
      _userServiceStatus = ApiHealthStatus.unhealthy;
      return false;
    }
  }
  
  Future<bool> checkAllServices() async {
    final gatewayHealthy = await checkApiGatewayHealth();
    final authHealthy = await checkAuthServiceHealth();
    final userHealthy = await checkUserServiceHealth();
    
    return gatewayHealthy && authHealthy && userHealthy;
  }
}

@GenerateMocks([Dio])
void main() {
  late ApiHealthService apiHealthService;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    apiHealthService = ApiHealthService(mockDio);
  });

  group('API健康检查服务测试', () {
    test('当API网关健康时应返回true', () async {
      when(mockDio.get('/api/health')).thenAnswer(
        (_) async => Response(
          statusCode: 200,
          requestOptions: RequestOptions(path: ''),
        ),
      );

      final result = await apiHealthService.checkApiGatewayHealth();
      expect(result, true);
      expect(apiHealthService.apiGatewayStatus, ApiHealthStatus.healthy);
    });

    test('当API网关不健康时应返回false', () async {
      when(mockDio.get('/api/health')).thenAnswer(
        (_) async => Response(
          statusCode: 500,
          requestOptions: RequestOptions(path: ''),
        ),
      );

      final result = await apiHealthService.checkApiGatewayHealth();
      expect(result, false);
      expect(apiHealthService.apiGatewayStatus, ApiHealthStatus.unhealthy);
    });

    test('当API网关请求异常时应返回false', () async {
      when(mockDio.get('/api/health')).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          type: DioExceptionType.connectionTimeout,
        ),
      );

      final result = await apiHealthService.checkApiGatewayHealth();
      expect(result, false);
      expect(apiHealthService.apiGatewayStatus, ApiHealthStatus.unhealthy);
    });

    test('当认证服务健康时应返回true', () async {
      when(mockDio.get('/auth/health')).thenAnswer(
        (_) async => Response(
          statusCode: 200,
          requestOptions: RequestOptions(path: ''),
        ),
      );

      final result = await apiHealthService.checkAuthServiceHealth();
      expect(result, true);
      expect(apiHealthService.authServiceStatus, ApiHealthStatus.healthy);
    });

    test('当用户服务健康时应返回true', () async {
      when(mockDio.get('/user/health')).thenAnswer(
        (_) async => Response(
          statusCode: 200,
          requestOptions: RequestOptions(path: ''),
        ),
      );

      final result = await apiHealthService.checkUserServiceHealth();
      expect(result, true);
      expect(apiHealthService.userServiceStatus, ApiHealthStatus.healthy);
    });

    test('当所有服务健康时checkAllServices应返回true', () async {
      when(mockDio.get('/api/health')).thenAnswer(
        (_) async => Response(
          statusCode: 200,
          requestOptions: RequestOptions(path: ''),
        ),
      );
      
      when(mockDio.get('/auth/health')).thenAnswer(
        (_) async => Response(
          statusCode: 200,
          requestOptions: RequestOptions(path: ''),
        ),
      );
      
      when(mockDio.get('/user/health')).thenAnswer(
        (_) async => Response(
          statusCode: 200,
          requestOptions: RequestOptions(path: ''),
        ),
      );

      final result = await apiHealthService.checkAllServices();
      expect(result, true);
      expect(apiHealthService.apiGatewayStatus, ApiHealthStatus.healthy);
      expect(apiHealthService.authServiceStatus, ApiHealthStatus.healthy);
      expect(apiHealthService.userServiceStatus, ApiHealthStatus.healthy);
    });

    test('当任一服务不健康时checkAllServices应返回false', () async {
      when(mockDio.get('/api/health')).thenAnswer(
        (_) async => Response(
          statusCode: 200,
          requestOptions: RequestOptions(path: ''),
        ),
      );
      
      when(mockDio.get('/auth/health')).thenAnswer(
        (_) async => Response(
          statusCode: 500,
          requestOptions: RequestOptions(path: ''),
        ),
      );
      
      when(mockDio.get('/user/health')).thenAnswer(
        (_) async => Response(
          statusCode: 200,
          requestOptions: RequestOptions(path: ''),
        ),
      );

      final result = await apiHealthService.checkAllServices();
      expect(result, false);
      expect(apiHealthService.apiGatewayStatus, ApiHealthStatus.healthy);
      expect(apiHealthService.authServiceStatus, ApiHealthStatus.unhealthy);
      expect(apiHealthService.userServiceStatus, ApiHealthStatus.healthy);
    });
  });
}