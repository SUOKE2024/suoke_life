#!/bin/bash

# 创建 core 库的目录结构
mkdir -p libs/core/lib/network
mkdir -p libs/core/lib/mocks

# 创建 core 库的 pubspec.yaml
cat > libs/core/pubspec.yaml << 'EOL'
name: core
description: Core library for Suoke Life
version: 1.0.0+1

environment:
  sdk: '>=3.3.0 <4.0.0'
  flutter: ">=3.16.0"

dependencies:
  flutter:
    sdk: flutter
  injectable: ^2.3.2
  get_it: ^7.6.0
  dio: ^5.4.0
  sqflite: ^2.3.0
  redis: ^4.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  test: ^1.24.9
  mockito: ^5.4.4
  build_runner: ^2.4.14
EOL

# 创建 mock 文件
cat > libs/core/lib/mocks/mock_http_client.dart << 'EOL'
import 'package:mockito/mockito.dart';
import 'package:core/network/http_client.dart';

class MockHttpClient extends Mock implements HttpClient {}
EOL

# 创建 http_client.dart
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