import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/core/utils/secure_storage.dart';
import 'package:suoke_life/core/utils/storage_keys.dart';
import 'package:suoke_life/data/datasources/auth_remote_data_source.dart';
import 'package:suoke_life/data/repositories/auth_repository_impl.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/data/datasources/remote/api_service.dart';
import 'package:suoke_life/data/datasources/remote/auth_api_service.dart';

import 'auth_repository_test.mocks.dart';

@GenerateMocks([AuthRemoteDataSource, NetworkInfo, SecureStorage, ApiService, AuthApiService])
void main() {
  late AuthRepositoryImpl repository;
  late MockAuthRemoteDataSource mockRemoteDataSource;
  late MockNetworkInfo mockNetworkInfo;
  late MockSecureStorage mockSecureStorage;
  late MockApiService mockApiService;
  late MockAuthApiService mockAuthApiService;

  setUp(() {
    mockRemoteDataSource = MockAuthRemoteDataSource();
    mockNetworkInfo = MockNetworkInfo();
    mockSecureStorage = MockSecureStorage();
    mockApiService = MockApiService();
    mockAuthApiService = MockAuthApiService();
    
    repository = AuthRepositoryImpl(
      remoteDataSource: mockRemoteDataSource,
      networkInfo: mockNetworkInfo,
      secureStorage: mockSecureStorage,
      apiService: mockApiService,
      authApiService: mockAuthApiService,
    );
  });

  group('登录', () {
    final tEmail = 'test@example.com';
    final tPassword = 'password123';
    final tUser = User(
      id: '123456',
      username: 'testuser',
      email: 'test@example.com',
      phoneNumber: '13800138000',
      displayName: '测试用户',
      avatarUrl: 'https://example.com/avatar.png',
      bio: '这是一个测试用户',
      role: 'user',
      createdAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
      updatedAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
    );
    final tAuthToken = AuthToken(
      accessToken: 'access_token',
      refreshToken: 'refresh_token',
      expiresIn: 3600,
    );

    test('应当检查网络连接', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.login(any, any))
          .thenAnswer((_) async => (tUser, tAuthToken));
      when(mockSecureStorage.write(any, any))
          .thenAnswer((_) async => {});

      // act
      await repository.login(tEmail, tPassword);

      // assert
      verify(mockNetworkInfo.isConnected);
    });

    group('设备在线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      });

      test('网络连接成功时，应当通过远程数据源登录并返回成功结果', () async {
        // arrange
        when(mockRemoteDataSource.login(any, any))
            .thenAnswer((_) async => (tUser, tAuthToken));
        when(mockSecureStorage.write(any, any))
            .thenAnswer((_) async => {});

        // act
        final result = await repository.login(tEmail, tPassword);

        // assert
        verify(mockRemoteDataSource.login(tEmail, tPassword));
        expect(result, equals(Right((tUser, tAuthToken))));
      });

      test('远程数据源抛出ServerException时，应当返回服务器错误', () async {
        // arrange
        when(mockRemoteDataSource.login(any, any))
            .thenThrow(ServerException(message: '登录失败', statusCode: 401));

        // act
        final result = await repository.login(tEmail, tPassword);

        // assert
        verify(mockRemoteDataSource.login(tEmail, tPassword));
        expect(result, equals(Left(ServerFailure(message: '登录失败'))));
      });
    });

    group('设备离线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      });

      test('网络连接失败时，应当返回网络错误', () async {
        // act
        final result = await repository.login(tEmail, tPassword);

        // assert
        verifyZeroInteractions(mockRemoteDataSource);
        expect(result, equals(Left(NetworkFailure(message: '无网络连接'))));
      });
    });
  });

  group('注册', () {
    final tRegisterData = {
      'username': 'newuser',
      'email': 'newuser@example.com',
      'password': 'password123',
      'phone_number': '13800138000',
      'display_name': '新用户',
    };
    final tUser = User(
      id: '123456',
      username: 'newuser',
      email: 'newuser@example.com',
      phoneNumber: '13800138000',
      displayName: '新用户',
      avatarUrl: '',
      bio: '',
      role: 'user',
      createdAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
      updatedAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
    );
    final tAuthToken = AuthToken(
      accessToken: 'access_token',
      refreshToken: 'refresh_token',
      expiresIn: 3600,
    );

    test('应当检查网络连接', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.register(any))
          .thenAnswer((_) async => (tUser, tAuthToken));
      when(mockSecureStorage.write(any, any))
          .thenAnswer((_) async => {});

      // act
      await repository.register(tRegisterData);

      // assert
      verify(mockNetworkInfo.isConnected);
    });

    group('设备在线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      });

      test('网络连接成功时，应当通过远程数据源注册并返回成功结果', () async {
        // arrange
        when(mockRemoteDataSource.register(any))
            .thenAnswer((_) async => (tUser, tAuthToken));
        when(mockSecureStorage.write(any, any))
            .thenAnswer((_) async => {});

        // act
        final result = await repository.register(tRegisterData);

        // assert
        verify(mockRemoteDataSource.register(tRegisterData));
        expect(result, equals(Right((tUser, tAuthToken))));
      });

      test('远程数据源抛出ServerException时，应当返回服务器错误', () async {
        // arrange
        when(mockRemoteDataSource.register(any))
            .thenThrow(ServerException(message: '注册失败', statusCode: 400));

        // act
        final result = await repository.register(tRegisterData);

        // assert
        verify(mockRemoteDataSource.register(tRegisterData));
        expect(result, equals(Left(ServerFailure(message: '注册失败'))));
      });
    });

    group('设备离线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      });

      test('网络连接失败时，应当返回网络错误', () async {
        // act
        final result = await repository.register(tRegisterData);

        // assert
        verifyZeroInteractions(mockRemoteDataSource);
        expect(result, equals(Left(NetworkFailure(message: '无网络连接'))));
      });
    });
  });

  group('刷新令牌', () {
    final tRefreshToken = 'refresh_token';
    final tAuthToken = AuthToken(
      accessToken: 'new_access_token',
      refreshToken: 'new_refresh_token',
      expiresIn: 3600,
    );

    test('应当检查网络连接', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.refreshToken(any))
          .thenAnswer((_) async => tAuthToken);
      when(mockSecureStorage.write(any, any))
          .thenAnswer((_) async => {});

      // act
      await repository.refreshToken(tRefreshToken);

      // assert
      verify(mockNetworkInfo.isConnected);
    });

    group('设备在线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      });

      test('网络连接成功时，应当通过远程数据源刷新令牌并返回成功结果', () async {
        // arrange
        when(mockRemoteDataSource.refreshToken(any))
            .thenAnswer((_) async => tAuthToken);
        when(mockSecureStorage.write(any, any))
            .thenAnswer((_) async => {});

        // act
        final result = await repository.refreshToken(tRefreshToken);

        // assert
        verify(mockRemoteDataSource.refreshToken(tRefreshToken));
        expect(result, equals(Right(tAuthToken)));
      });

      test('远程数据源抛出ServerException时，应当返回服务器错误', () async {
        // arrange
        when(mockRemoteDataSource.refreshToken(any))
            .thenThrow(ServerException(message: '令牌刷新失败', statusCode: 401));

        // act
        final result = await repository.refreshToken(tRefreshToken);

        // assert
        verify(mockRemoteDataSource.refreshToken(tRefreshToken));
        expect(result, equals(Left(ServerFailure(message: '令牌刷新失败'))));
      });
    });

    group('设备离线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      });

      test('网络连接失败时，应当返回网络错误', () async {
        // act
        final result = await repository.refreshToken(tRefreshToken);

        // assert
        verifyZeroInteractions(mockRemoteDataSource);
        expect(result, equals(Left(NetworkFailure(message: '无网络连接'))));
      });
    });
  });

  group('登出', () {
    test('应当检查网络连接', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.logout())
          .thenAnswer((_) async => true);
      when(mockSecureStorage.delete(any))
          .thenAnswer((_) async => {});

      // act
      await repository.logout();

      // assert
      verify(mockNetworkInfo.isConnected);
    });

    group('设备在线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      });

      test('网络连接成功时，应当通过远程数据源登出并返回成功结果', () async {
        // arrange
        when(mockRemoteDataSource.logout())
            .thenAnswer((_) async => true);
        when(mockSecureStorage.delete(any))
            .thenAnswer((_) async => {});

        // act
        final result = await repository.logout();

        // assert
        verify(mockRemoteDataSource.logout());
        expect(result, equals(const Right(true)));
      });

      test('远程数据源抛出ServerException时，应当返回服务器错误', () async {
        // arrange
        when(mockRemoteDataSource.logout())
            .thenThrow(ServerException(message: '登出失败', statusCode: 500));

        // act
        final result = await repository.logout();

        // assert
        verify(mockRemoteDataSource.logout());
        expect(result, equals(Left(ServerFailure(message: '登出失败'))));
      });
    });

    group('设备离线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      });

      test('网络连接失败时，应当返回网络错误', () async {
        // act
        final result = await repository.logout();

        // assert
        verifyZeroInteractions(mockRemoteDataSource);
        expect(result, equals(Left(NetworkFailure(message: '无网络连接'))));
      });
    });
  });
} 