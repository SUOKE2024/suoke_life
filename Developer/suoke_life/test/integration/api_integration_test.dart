import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:suoke_life/core/constants/api_constants.dart';

void main() {
  late Dio dio;

  setUp(() {
    dio = Dio(BaseOptions(
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 5),
    ));
  });

  group('API集成测试', () {
    test('API网关健康检查', () async {
      try {
        final response = await dio.get('${ApiConstants.apiBaseUrl}/health');
        expect(response.statusCode, 200);
        expect(response.data, containsPair('status', 'healthy'));
        print('API网关健康检查通过');
      } catch (e) {
        fail('API网关健康检查失败: $e');
      }
    });

    test('认证服务健康检查', () async {
      try {
        final response = await dio.get('${ApiConstants.authServiceUrl}/health');
        expect(response.statusCode, 200);
        expect(response.data, containsPair('status', 'healthy'));
        print('认证服务健康检查通过');
      } catch (e) {
        fail('认证服务健康检查失败: $e');
      }
    });

    test('用户服务健康检查', () async {
      try {
        final response = await dio.get('${ApiConstants.userServiceUrl}/health');
        expect(response.statusCode, 200);
        expect(response.data, containsPair('status', 'healthy'));
        print('用户服务健康检查通过');
      } catch (e) {
        fail('用户服务健康检查失败: $e');
      }
    });

    test('用户登录接口测试', () async {
      try {
        final response = await dio.post(
          '${ApiConstants.authServiceUrl}/api/v1/auth/login',
          data: {
            'username': 'test_user',
            'password': 'test_password',
          },
        );
        
        // 这里我们只验证接口是否正常响应，不验证实际登录成功
        // 在集成测试环境中，我们应该有专门的测试账户
        expect(response.statusCode, anyOf(200, 401, 403));
        print('用户登录接口测试通过');
      } catch (e) {
        fail('用户登录接口测试失败: $e');
      }
    });

    test('用户注册接口测试', () async {
      final testUsername = 'test_user_${DateTime.now().millisecondsSinceEpoch}';
      
      try {
        final response = await dio.post(
          '${ApiConstants.userServiceUrl}/api/v1/users',
          data: {
            'username': testUsername,
            'password': 'Test@123',
            'email': '$testUsername@example.com',
            'phone': '13800138000',
          },
        );
        
        // 同样只验证接口响应，不验证实际结果
        expect(response.statusCode, anyOf(200, 201, 400, 409));
        print('用户注册接口测试通过');
      } catch (e) {
        fail('用户注册接口测试失败: $e');
      }
    });
  });
}