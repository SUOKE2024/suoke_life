// 网络服务提供者文件
// 定义网络相关的Provider

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/core/network/http_client.dart';
import 'package:suoke_life/core/network/network_info.dart';
import '../providers/core_providers.dart';

/// API客户端提供者
final apiClientProvider = Provider<ApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  final networkInfo = ref.watch(networkInfoProvider);
  return ApiClient(dio: dio, networkInfo: networkInfo);
});

/// HTTP客户端提供者
final httpClientProvider = Provider<HttpClient>((ref) {
  final dio = ref.watch(dioProvider);
  final networkInfo = ref.watch(networkInfoProvider);
  return HttpClient(dio: dio, networkInfo: networkInfo);
});

/// WebSocket基础URL提供者
final webSocketBaseUrlProvider = Provider<String>((ref) {
  // 根据环境变量或配置决定WebSocket URL
  const bool isProduction = bool.fromEnvironment('dart.vm.product');
  return isProduction
    ? 'wss://api.suoke.life/ws'
    : 'ws://118.31.223.213/ws';
});

/// WebSocket客户端Factory提供者
final webSocketClientFactoryProvider = Provider<WebSocketClientFactory>((ref) {
  final baseUrl = ref.watch(webSocketBaseUrlProvider);
  return WebSocketClientFactory(baseUrl: baseUrl);
});

/// WebSocket客户端工厂
class WebSocketClientFactory {
  final String baseUrl;

  WebSocketClientFactory({required this.baseUrl});

  // 根据agentId创建不同的WebSocket连接
  Future<WebSocketClient> createClient(String agentId) async {
    final endpoint = '$baseUrl/agent/$agentId';
    return WebSocketClient(url: endpoint);
  }
}

/// WebSocket客户端
class WebSocketClient {
  final String url;
  
  WebSocketClient({required this.url});
  
  // WebSocket实现方法
  // 这里将根据实际需求实现连接、发送消息等功能
} 