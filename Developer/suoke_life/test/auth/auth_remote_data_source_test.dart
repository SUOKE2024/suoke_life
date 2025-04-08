import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/data/datasources/auth_remote_data_source_impl.dart';
import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/data/models/auth_token_model.dart';

import 'auth_remote_data_source_test.mocks.dart';

@GenerateMocks([http.Client])
void main() {
  late AuthRemoteDataSourceImpl dataSource;
  late MockClient mockHttpClient;

  setUp(() {
    mockHttpClient = MockClient();
    dataSource = AuthRemoteDataSourceImpl(
      client: mockHttpClient,
      baseUrl: ApiConstants.baseUrl,
    );
  });

  group('login', () {
    final tEmail = 'test@example.com';
    final tPassword = 'password123';
    final tUserJson = {
      'id': '123456',
      'username': 'testuser',
      'email': 'test@example.com',
      'phone_number': '13800138000',
      'display_name': '测试用户',
      'avatar_url': 'https://example.com/avatar.png',
      'bio': '这是一个测试用户',
      'role': 'user',
      'created_at': '2023-01-01T00:00:00.000Z',
      'updated_at': '2023-01-01T00:00:00.000Z',
    };
    final tTokenJson = {
      'access_token': 'access_token',
      'refresh_token': 'refresh_token',
      'expires_in': 3600,
    };
    final tResponseJson = {
      'user': tUserJson,
      'token': tTokenJson,
    };
    final tUserModel = UserModel(
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
    final tTokenModel = AuthTokenModel(
      accessToken: 'access_token',
      refreshToken: 'refresh_token',
      expiresIn: 3600,
    );

    test('应当发起正确的POST请求', () async {
      // arrange
      when(mockHttpClient.post(
        any,
        headers: anyNamed('headers'),
        body: anyNamed('body'),
      )).thenAnswer(
        (_) async => http.Response(json.encode(tResponseJson), 200),
      );

      // act
      await dataSource.login(tEmail, tPassword);

      // assert
      verify(mockHttpClient.post(
        Uri.parse('${ApiConstants.baseUrl}${ApiConstants.auth}/login'),
        headers: any(named: 'headers'),
        body: json.encode({
          'email': tEmail,
          'password': tPassword,
        }),
      ));
    });

    test('响应码为200时应返回用户模型和认证令牌模型', () async {
      // arrange
      when(mockHttpClient.post(
        any,
        headers: anyNamed('headers'),
        body: anyNamed('body'),
      )).thenAnswer(
        (_) async => http.Response(json.encode(tResponseJson), 200),
      );

      // act
      final result = await dataSource.login(tEmail, tPassword);

      // assert
      expect(result.$1, equals(tUserModel));
      expect(result.$2, equals(tTokenModel));
    });

    test('响应码非200时应抛出ServerException', () async {
      // arrange
      when(mockHttpClient.post(
        any,
        headers: anyNamed('headers'),
        body: anyNamed('body'),
      )).thenAnswer(
        (_) async => http.Response(
          json.encode({'message': '登录失败'}),
          401,
        ),
      );

      // act
      final call = dataSource.login;

      // assert
      expect(
        () => call(tEmail, tPassword),
        throwsA(isA<ServerException>()),
      );
    });
  });

  group('refreshToken', () {
    final tRefreshToken = 'refresh_token';
    final tTokenJson = {
      'token': {
        'access_token': 'new_access_token',
        'refresh_token': 'new_refresh_token',
        'expires_in': 3600,
      }
    };
    final tTokenModel = AuthTokenModel(
      accessToken: 'new_access_token',
      refreshToken: 'new_refresh_token',
      expiresIn: 3600,
    );

    test('应当发起正确的POST请求', () async {
      // arrange
      when(mockHttpClient.post(
        any,
        headers: anyNamed('headers'),
        body: anyNamed('body'),
      )).thenAnswer(
        (_) async => http.Response(json.encode(tTokenJson), 200),
      );

      // act
      await dataSource.refreshToken(tRefreshToken);

      // assert
      verify(mockHttpClient.post(
        Uri.parse('${ApiConstants.baseUrl}${ApiConstants.auth}/refresh'),
        headers: any(named: 'headers'),
        body: json.encode({
          'refresh_token': tRefreshToken,
        }),
      ));
    });

    test('响应码为200时应返回新的认证令牌模型', () async {
      // arrange
      when(mockHttpClient.post(
        any,
        headers: anyNamed('headers'),
        body: anyNamed('body'),
      )).thenAnswer(
        (_) async => http.Response(json.encode(tTokenJson), 200),
      );

      // act
      final result = await dataSource.refreshToken(tRefreshToken);

      // assert
      expect(result, equals(tTokenModel));
    });

    test('响应码非200时应抛出ServerException', () async {
      // arrange
      when(mockHttpClient.post(
        any,
        headers: anyNamed('headers'),
        body: anyNamed('body'),
      )).thenAnswer(
        (_) async => http.Response(
          json.encode({'message': '令牌刷新失败'}),
          401,
        ),
      );

      // act
      final call = dataSource.refreshToken;

      // assert
      expect(
        () => call(tRefreshToken),
        throwsA(isA<ServerException>()),
      );
    });
  });

  group('logout', () {
    test('应当发起正确的POST请求', () async {
      // arrange
      when(mockHttpClient.post(
        any,
        headers: anyNamed('headers'),
      )).thenAnswer(
        (_) async => http.Response('', 200),
      );

      // act
      await dataSource.logout();

      // assert
      verify(mockHttpClient.post(
        Uri.parse('${ApiConstants.baseUrl}${ApiConstants.auth}/logout'),
        headers: any(named: 'headers'),
      ));
    });

    test('响应码为200时应返回true', () async {
      // arrange
      when(mockHttpClient.post(
        any,
        headers: anyNamed('headers'),
      )).thenAnswer(
        (_) async => http.Response('', 200),
      );

      // act
      final result = await dataSource.logout();

      // assert
      expect(result, equals(true));
    });

    test('响应码非200时应抛出ServerException', () async {
      // arrange
      when(mockHttpClient.post(
        any,
        headers: anyNamed('headers'),
      )).thenAnswer(
        (_) async => http.Response(
          json.encode({'message': '登出失败'}),
          500,
        ),
      );

      // act
      final call = dataSource.logout;

      // assert
      expect(
        () => call(),
        throwsA(isA<ServerException>()),
      );
    });
  });
} 