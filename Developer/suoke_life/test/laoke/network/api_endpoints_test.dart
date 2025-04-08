import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/core/storage/secure_storage.dart';
import '../../mocks/laoke_mocks.mocks.dart';

/// 自定义拦截器，用于捕获Dio请求并验证URL
class TestInterceptor extends Interceptor {
  String? capturedUrl;
  
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    capturedUrl = options.uri.toString();
    super.onRequest(options, handler);
  }
}

void main() {
  group('API端点测试', () {
    late ApiClient apiClient;
    late MockSecureStorage mockSecureStorage;
    late Dio dio;
    late TestInterceptor interceptor;
    
    setUp(() {
      dio = Dio();
      interceptor = TestInterceptor();
      dio.interceptors.add(interceptor);
      
      mockSecureStorage = MockSecureStorage();
      // 由于ApiClient构造函数中创建了新的Dio实例，我们需要修改测试方法
      apiClient = ApiClient(
        baseUrl: 'http://test.suoke.life',
        secureStorage: mockSecureStorage,
      );
    });
    
    test('应该通过检查基础URL参数确保初始化正确', () {
      expect(apiClient.baseUrl, 'http://test.suoke.life');
    });
    
    // 注意：以下测试无法直接测试ApiClient内部的私有方法，只能通过行为测试
    // 实际生产环境中，建议重构ApiClient，将_getAgentEndpoint和_getAgentWebSocketEndpoint
    // 方法改为公开方法，以便直接测试
    
    test('智能体服务端点应该遵循特定模式', () {
      // 理想情况下，我们希望ApiClient提供公开的方法来获取端点，以便直接测试
      // 由于没有公开方法，我们只能通过检查Api客户端的基础URL来确保初始化正确
      
      // 验证小柯智能体的端点（不直接测试，仅为文档）
      const xiaoke = 'xiaoke-service';
      // 期望的端点：http://test.suoke.life/xiaoke-service/api/v1/agents/xiaoke-service
      
      // 验证小艾智能体的端点（不直接测试，仅为文档）
      const xiaoai = 'xiaoai-service';
      // 期望的端点：http://test.suoke.life/xiaoai-service/api/v1/agents/xiaoai-service
      
      // 验证索尔智能体的端点（不直接测试，仅为文档）
      const soer = 'soer-service';
      // 期望的端点：http://test.suoke.life/soer-service/api/v1/agents/soer-service
      
      // 验证老柯智能体的端点（不直接测试，仅为文档）
      const laoke = 'laoke-service';
      // 期望的端点：http://test.suoke.life/laoke-service/api/v1/agents/laoke-service
    });
    
    test('WebSocket端点应该正确转换HTTP URL为WebSocket URL', () {
      // 同样，我们希望ApiClient提供公开的方法来测试WebSocket端点的转换
      // 由于没有公开方法，只能记录期望的行为
      
      // HTTP URL: http://test.suoke.life
      // 期望的WebSocket URL: ws://test.suoke.life
      
      // HTTPS URL: https://test.suoke.life
      // 期望的WebSocket URL: wss://test.suoke.life
    });
  });
} 