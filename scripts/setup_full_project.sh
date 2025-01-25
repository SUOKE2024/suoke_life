#!/bin/bash

# 创建基本目录结构
source scripts/create_test_dirs.sh

# 创建 core 库的网络相关文件
cat > libs/core/lib/network/http_client.dart << 'EOL'
import 'package:injectable/injectable.dart';

abstract class HttpClient {
  Future<dynamic> get(String url);
  Future<dynamic> post(String url, dynamic data);
}

@Injectable(as: HttpClient)
class HttpClientImpl implements HttpClient {
  @override
  Future get(String url) async {
    // TODO: Implement get
    return null;
  }

  @override
  Future post(String url, dynamic data) async {
    // TODO: Implement post
    return null;
  }
}
EOL

# 创建 mock 文件
cat > libs/core/test/mocks/mock_http_client.dart << 'EOL'
import 'package:mockito/mockito.dart';
import 'package:core/network/http_client.dart';

class MockHttpClient extends Mock implements HttpClient {}
EOL

# 创建用户服务相关文件
cat > apps/user_service/lib/services/payment_service.dart << 'EOL'
import 'package:injectable/injectable.dart';
import 'package:core/network/http_client.dart';
import 'package:core/network/api_response.dart';

abstract class PaymentService {
  Future<ApiResponse> processPayment(String orderId, double amount);
}

@Injectable(as: PaymentService)
class PaymentServiceImpl implements PaymentService {
  final HttpClient _client;

  PaymentServiceImpl(this._client);

  @override
  Future<ApiResponse> processPayment(String orderId, double amount) async {
    try {
      final response = await _client.post('/payment', {
        'orderId': orderId,
        'amount': amount,
      });
      return ApiResponse.success(response);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }
}
EOL

# 创建测试文件
cat > apps/user_service/test/services/payment_service_test.dart << 'EOL'
import 'package:test/test.dart';
import 'package:mockito/annotations.dart';
import 'package:core/network/http_client.dart';
import 'package:user_service/services/payment_service.dart';
import 'package:core/test/mocks/mock_http_client.dart';

void main() {
  late PaymentService paymentService;
  late MockHttpClient mockClient;

  setUp(() {
    mockClient = MockHttpClient();
    paymentService = PaymentServiceImpl(mockClient);
  });

  test('processPayment returns success response', () async {
    final response = await paymentService.processPayment('order123', 100.0);
    expect(response.success, isTrue);
  });
}
EOL

# 创建 pubspec.yaml 文件
cat > apps/user_service/pubspec.yaml << 'EOL'
name: user_service
description: User Service for Suoke Life
version: 1.0.0+1

environment:
  sdk: '>=3.3.0 <4.0.0'
  flutter: ">=3.16.0"

dependencies:
  flutter:
    sdk: flutter
  core:
    path: ../../libs/core
  injectable: ^2.3.2
  get_it: ^7.6.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  test: ^1.24.9
  mockito: ^5.4.4
  build_runner: ^2.4.14
EOL 