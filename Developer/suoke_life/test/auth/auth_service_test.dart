import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:suoke_life/data/repositories/auth_repository_impl.dart';
import 'package:suoke_life/data/datasources/local/auth_local_data_source.dart';
import 'package:suoke_life/data/datasources/remote/auth_api_service.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/usecases/auth_usecases.dart';
import 'package:suoke_life/core/exceptions/auth_exceptions.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// 生成Mock类
@GenerateMocks([AuthApiService, AuthLocalDataSource, FlutterSecureStorage])
import 'auth_service_test.mocks.dart';

import 'auth_repository_test.dart' as auth_repository_test;
import 'auth_remote_data_source_test.dart' as auth_remote_data_source_test;
import 'refresh_token_test.dart' as refresh_token_test;

void main() {
  group('认证服务测试', () {
    group('1. 认证存储库测试', () {
      auth_repository_test.main();
    });

    group('2. 认证远程数据源测试', () {
      auth_remote_data_source_test.main();
    });

    group('3. 刷新令牌用例测试', () {
      refresh_token_test.main();
    });
  });
} 