import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/data/datasources/user_remote_data_source.dart';
import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/data/models/user_preferences_model.dart';

import 'user_remote_data_source_test.mocks.dart';

/// 只实现两个主要方法的测试实现
class UserRemoteDataSourceTestImpl implements UserRemoteDataSource {
  final http.Client client;
  final String baseUrl;
  final Map<String, String> headers = {'Content-Type': 'application/json'};

  UserRemoteDataSourceTestImpl({
    required this.client,
    required this.baseUrl,
  });

  @override
  Future<UserModel> getUserProfile(String userId) async {
    final uri = Uri.parse('$baseUrl${ApiConstants.users}/$userId');
    final response = await client.get(
      uri,
      headers: headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return UserModel.fromJson(json['data']);
    } else {
      throw ServerException(
        message: jsonDecode(response.body)['message'] ?? '获取用户资料失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<UserModel> updateUserProfile(String userId, Map<String, dynamic> profileData) async {
    final uri = Uri.parse('$baseUrl${ApiConstants.users}/$userId');
    final response = await client.put(
      uri,
      headers: headers,
      body: jsonEncode(profileData),
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return UserModel.fromJson(json['data']);
    } else {
      throw ServerException(
        message: jsonDecode(response.body)['message'] ?? '更新用户资料失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<UserPreferencesModel> getUserPreferences(String userId) async {
    final uri = Uri.parse('$baseUrl${ApiConstants.users}/$userId/preferences');
    final response = await client.get(
      uri,
      headers: headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return UserPreferencesModel.fromJson(json['data']);
    } else {
      throw ServerException(
        message: jsonDecode(response.body)['message'] ?? '获取用户偏好设置失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  Future<UserPreferencesModel> updateUserPreferences(String userId, Map<String, dynamic> preferences) async {
    final uri = Uri.parse('$baseUrl${ApiConstants.users}/$userId/preferences');
    final response = await client.put(
      uri,
      headers: headers,
      body: jsonEncode(preferences),
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return UserPreferencesModel.fromJson(json['data']);
    } else {
      throw ServerException(
        message: jsonDecode(response.body)['message'] ?? '更新用户偏好设置失败',
        statusCode: response.statusCode,
      );
    }
  }

  @override
  dynamic noSuchMethod(Invocation invocation) {
    return super.noSuchMethod(invocation);
  }
}

@GenerateMocks([http.Client])
void main() {
  late UserRemoteDataSourceTestImpl dataSource;
  late MockClient mockHttpClient;
  final headers = {'Content-Type': 'application/json'};

  setUp(() {
    mockHttpClient = MockClient();
    dataSource = UserRemoteDataSourceTestImpl(
      client: mockHttpClient,
      baseUrl: ApiConstants.baseUrl,
    );
  });

  group('getUserProfile', () {
    final userId = '123456';
    final tUserJson = {
      'status': 'success',
      'data': {
        'id': userId,
        'username': 'testuser',
        'email': 'test@example.com',
        'phone_number': '13800138000',
        'display_name': '测试用户',
        'avatar_url': 'https://example.com/avatar.png',
        'created_at': '2023-01-01T00:00:00.000Z',
        'updated_at': '2023-01-01T00:00:00.000Z',
      }
    };
    final tUserModel = UserModel(
      id: userId,
      username: 'testuser',
      email: 'test@example.com',
      phoneNumber: '13800138000',
      displayName: '测试用户',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
      updatedAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
    );

    test('应当发起正确的GET请求', () async {
      // arrange
      when(mockHttpClient.get(any, headers: headers)).thenAnswer(
        (_) async => http.Response(json.encode(tUserJson), 200),
      );

      // act
      await dataSource.getUserProfile(userId);

      // assert
      verify(mockHttpClient.get(
        Uri.parse('${ApiConstants.baseUrl}${ApiConstants.users}/$userId'),
        headers: headers,
      ));
    });

    test('响应码为200时应返回用户模型', () async {
      // arrange
      when(mockHttpClient.get(any, headers: headers)).thenAnswer(
        (_) async => http.Response(json.encode(tUserJson), 200),
      );

      // act
      final result = await dataSource.getUserProfile(userId);

      // assert
      expect(result, equals(tUserModel));
    });

    test('响应码非200时应抛出ServerException', () async {
      // arrange
      when(mockHttpClient.get(any, headers: headers)).thenAnswer(
        (_) async => http.Response(
          json.encode({'message': '用户不存在'}),
          404,
        ),
      );

      // act
      final call = dataSource.getUserProfile;

      // assert
      expect(() => call(userId), throwsA(isA<ServerException>()));
    });
  });

  group('updateUserProfile', () {
    final userId = '123456';
    final profileData = {
      'display_name': '测试用户 (已更新)',
      'avatar_url': 'https://example.com/new-avatar.png',
    };
    final tUpdateUserJson = {
      'status': 'success',
      'data': {
        'id': userId,
        'username': 'testuser',
        'email': 'test@example.com',
        'phone_number': '13800138000',
        'display_name': '测试用户 (已更新)',
        'avatar_url': 'https://example.com/new-avatar.png',
        'created_at': '2023-01-01T00:00:00.000Z',
        'updated_at': '2023-01-02T00:00:00.000Z',
      }
    };
    final tUpdatedUserModel = UserModel(
      id: userId,
      username: 'testuser',
      email: 'test@example.com',
      phoneNumber: '13800138000',
      displayName: '测试用户 (已更新)',
      avatarUrl: 'https://example.com/new-avatar.png',
      createdAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
      updatedAt: DateTime.parse('2023-01-02T00:00:00.000Z'),
    );

    test('应当发起正确的PUT请求', () async {
      // arrange
      when(mockHttpClient.put(
        any,
        headers: headers,
        body: any,
      )).thenAnswer(
        (_) async => http.Response(json.encode(tUpdateUserJson), 200),
      );

      // act
      await dataSource.updateUserProfile(userId, profileData);

      // assert
      verify(mockHttpClient.put(
        Uri.parse('${ApiConstants.baseUrl}${ApiConstants.users}/$userId'),
        headers: headers,
        body: json.encode(profileData),
      ));
    });

    test('响应码为200时应返回更新后的用户模型', () async {
      // arrange
      when(mockHttpClient.put(
        any,
        headers: headers,
        body: any,
      )).thenAnswer(
        (_) async => http.Response(json.encode(tUpdateUserJson), 200),
      );

      // act
      final result = await dataSource.updateUserProfile(userId, profileData);

      // assert
      expect(result, equals(tUpdatedUserModel));
    });

    test('响应码非200时应抛出ServerException', () async {
      // arrange
      when(mockHttpClient.put(
        any,
        headers: headers,
        body: any,
      )).thenAnswer(
        (_) async => http.Response(
          json.encode({'message': '未授权操作'}),
          401,
        ),
      );

      // act
      final call = dataSource.updateUserProfile;

      // assert
      expect(
        () => call(userId, profileData),
        throwsA(isA<ServerException>()),
      );
    });
  });

  group('getUserPreferences', () {
    final userId = '123456';
    final tPreferencesJson = {
      'data': {
        'user_id': userId,
        'theme_mode': 'dark',
        'language': 'zh',
        'notifications_enabled': true,
        'data_collection_consent': true,
        'created_at': '2023-01-01T00:00:00.000Z',
        'updated_at': '2023-01-01T00:00:00.000Z',
      }
    };
    final tPreferencesModel = UserPreferencesModel(
      userId: userId,
      themeMode: 'dark',
      language: 'zh',
      notificationsEnabled: true,
      dataCollectionConsent: true,
      createdAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
      updatedAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
    );

    test('应当发起正确的GET请求', () async {
      // arrange
      when(mockHttpClient.get(any, headers: headers)).thenAnswer(
        (_) async => http.Response(json.encode(tPreferencesJson), 200),
      );

      // act
      await dataSource.getUserPreferences(userId);

      // assert
      verify(mockHttpClient.get(
        Uri.parse('${ApiConstants.baseUrl}${ApiConstants.users}/$userId/preferences'),
        headers: headers,
      ));
    });

    test('响应码为200时应返回用户偏好设置模型', () async {
      // arrange
      when(mockHttpClient.get(any, headers: headers)).thenAnswer(
        (_) async => http.Response(json.encode(tPreferencesJson), 200),
      );

      // act
      final result = await dataSource.getUserPreferences(userId);

      // assert
      expect(result, equals(tPreferencesModel));
    });

    test('响应码非200时应抛出ServerException', () async {
      // arrange
      when(mockHttpClient.get(any, headers: headers)).thenAnswer(
        (_) async => http.Response(
          json.encode({'message': '用户偏好设置不存在'}),
          404,
        ),
      );

      // act
      final call = dataSource.getUserPreferences;

      // assert
      expect(() => call(userId), throwsA(isA<ServerException>()));
    });
  });

  group('updateUserPreferences', () {
    final userId = '123456';
    final preferences = {
      'theme_mode': 'light',
      'language': 'en',
      'notifications_enabled': false,
    };
    final tPreferencesJson = {
      'data': {
        'user_id': userId,
        'theme_mode': 'light',
        'language': 'en',
        'notifications_enabled': false,
        'data_collection_consent': true,
        'created_at': '2023-01-01T00:00:00.000Z',
        'updated_at': '2023-01-02T00:00:00.000Z',
      }
    };
    final tPreferencesModel = UserPreferencesModel(
      userId: userId,
      themeMode: 'light',
      language: 'en',
      notificationsEnabled: false,
      dataCollectionConsent: true,
      createdAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
      updatedAt: DateTime.parse('2023-01-02T00:00:00.000Z'),
    );

    test('应当发起正确的PUT请求', () async {
      // arrange
      when(mockHttpClient.put(
        any,
        headers: headers,
        body: any,
      )).thenAnswer(
        (_) async => http.Response(json.encode(tPreferencesJson), 200),
      );

      // act
      await dataSource.updateUserPreferences(userId, preferences);

      // assert
      verify(mockHttpClient.put(
        Uri.parse('${ApiConstants.baseUrl}${ApiConstants.users}/$userId/preferences'),
        headers: headers,
        body: json.encode(preferences),
      ));
    });

    test('响应码为200时应返回更新后的用户偏好设置模型', () async {
      // arrange
      when(mockHttpClient.put(
        any,
        headers: headers,
        body: any,
      )).thenAnswer(
        (_) async => http.Response(json.encode(tPreferencesJson), 200),
      );

      // act
      final result = await dataSource.updateUserPreferences(userId, preferences);

      // assert
      expect(result, equals(tPreferencesModel));
    });

    test('响应码非200时应抛出ServerException', () async {
      // arrange
      when(mockHttpClient.put(
        any,
        headers: headers,
        body: any,
      )).thenAnswer(
        (_) async => http.Response(
          json.encode({'message': '未授权操作'}),
          401,
        ),
      );

      // act
      final call = dataSource.updateUserPreferences;

      // assert
      expect(
        () => call(userId, preferences),
        throwsA(isA<ServerException>()),
      );
    });
  });
} 