import 'dart:io';
import 'package:flutter/foundation.dart';

class HTTP2Config {
  static Future<SecurityContext> createSecurityContext() async {
    final context = SecurityContext(withTrustedRoots: true);
    
    try {
      // 启用 HTTP/2 支持
      context.setAlpnProtocols(['h2', 'http/1.1'], true);
      
      // 设置 TLS 配置
      context.useCertificateChain('path/to/cert.pem');
      context.usePrivateKey('path/to/key.pem');
      
      return context;
    } catch (e) {
      debugPrint('Failed to create security context: $e');
      rethrow;
    }
  }

  static HttpClient createHttpClient() {
    final client = HttpClient();
    
    // 启用 HTTP/2
    client.connectionFactory = (
      Uri uri,
      String? proxyHost,
      int? proxyPort,
    ) async {
      final socket = await SecureSocket.connect(
        uri.host,
        uri.port,
        context: await createSecurityContext(),
        supportedProtocols: ['h2', 'http/1.1'],
      );
      
      return socket;
    };

    // 配置超时
    client.idleTimeout = const Duration(seconds: 30);
    client.connectionTimeout = const Duration(seconds: 30);
    
    return client;
  }
} 