import 'package:flutter_test/flutter_test.dart';

/// 模拟API客户端中的端点构造逻辑
class ApiEndpointTester {
  final String baseUrl;
  
  ApiEndpointTester(this.baseUrl);
  
  String getAgentEndpoint(String agentId) {
    switch (agentId) {
      case 'xiaoke-service':
        return '$baseUrl/xiaoke-service/api/v1/agents/$agentId';
      case 'xiaoai-service':
        return '$baseUrl/xiaoai-service/api/v1/agents/$agentId';
      case 'soer-service':
        return '$baseUrl/soer-service/api/v1/agents/$agentId';
      case 'laoke-service':
        return '$baseUrl/laoke-service/api/v1/agents/$agentId';
      default:
        return '$baseUrl/api/v1/agents/$agentId';
    }
  }
  
  String getAgentWebSocketEndpoint(String agentId) {
    String wsBaseUrl = baseUrl.replaceFirst(RegExp(r'^http'), 'ws');
    
    switch (agentId) {
      case 'xiaoke-service':
        return '$wsBaseUrl/xiaoke-service/api/v1/agents/$agentId/stream';
      case 'xiaoai-service':
        return '$wsBaseUrl/xiaoai-service/api/v1/agents/$agentId/stream';
      case 'soer-service':
        return '$wsBaseUrl/soer-service/api/v1/agents/$agentId/stream';
      case 'laoke-service':
        return '$wsBaseUrl/laoke-service/api/v1/agents/$agentId/stream';
      default:
        return '$wsBaseUrl/api/v1/agents/$agentId/stream';
    }
  }
}

void main() {
  group('API端点测试', () {
    late ApiEndpointTester tester;
    
    setUp(() {
      tester = ApiEndpointTester('http://test.suoke.life');
    });
    
    test('小柯智能体端点应该正确构造', () {
      final endpoint = tester.getAgentEndpoint('xiaoke-service');
      expect(endpoint, 'http://test.suoke.life/xiaoke-service/api/v1/agents/xiaoke-service');
    });
    
    test('小艾智能体端点应该正确构造', () {
      final endpoint = tester.getAgentEndpoint('xiaoai-service');
      expect(endpoint, 'http://test.suoke.life/xiaoai-service/api/v1/agents/xiaoai-service');
    });
    
    test('索尔智能体端点应该正确构造', () {
      final endpoint = tester.getAgentEndpoint('soer-service');
      expect(endpoint, 'http://test.suoke.life/soer-service/api/v1/agents/soer-service');
    });
    
    test('老柯智能体端点应该正确构造', () {
      final endpoint = tester.getAgentEndpoint('laoke-service');
      expect(endpoint, 'http://test.suoke.life/laoke-service/api/v1/agents/laoke-service');
    });
    
    test('默认智能体端点应该正确构造', () {
      final endpoint = tester.getAgentEndpoint('unknown-service');
      expect(endpoint, 'http://test.suoke.life/api/v1/agents/unknown-service');
    });
    
    test('WebSocket端点应该正确转换HTTP URL为WebSocket URL', () {
      final wsEndpoint = tester.getAgentWebSocketEndpoint('xiaoke-service');
      expect(wsEndpoint, 'ws://test.suoke.life/xiaoke-service/api/v1/agents/xiaoke-service/stream');
    });
    
    test('WebSocket端点应该正确转换HTTPS URL为WSS URL', () {
      final httpsTester = ApiEndpointTester('https://secure.suoke.life');
      final wssEndpoint = httpsTester.getAgentWebSocketEndpoint('xiaoke-service');
      expect(wssEndpoint, 'wss://secure.suoke.life/xiaoke-service/api/v1/agents/xiaoke-service/stream');
    });
  });
} 