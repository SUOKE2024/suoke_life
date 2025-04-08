import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/data/datasources/user_remote_data_source.dart';
import 'package:suoke_life/data/models/user_model.dart';
import 'package:suoke_life/data/repositories/user_repository_impl.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/entities/user_preferences.dart';

import 'mocks.mocks.dart';

@GenerateMocks([UserRemoteDataSource, NetworkInfo])
void main() {
  late UserRepositoryImpl repository;
  late MockUserRemoteDataSource mockRemoteDataSource;
  late MockNetworkInfo mockNetworkInfo;

  setUp(() {
    mockRemoteDataSource = MockUserRemoteDataSource();
    mockNetworkInfo = MockNetworkInfo();
    repository = UserRepositoryImpl(
      remoteDataSource: mockRemoteDataSource,
      networkInfo: mockNetworkInfo,
    );
  });

  final tUserId = 'user123';
  final tUserModel = UserModel(
    id: tUserId,
    username: '张三',
    email: 'zhangsan@example.com',
    phoneNumber: '13800138000',
    displayName: '张三',
    avatarUrl: 'https://example.com/avatar.jpg',
    createdAt: DateTime.parse('2023-01-01T00:00:00Z'),
    updatedAt: DateTime.parse('2023-01-02T00:00:00Z'),
  );

  final tUpdatedUserModel = UserModel(
    id: tUserId,
    username: '张三(已更新)',
    email: 'zhangsan@example.com',
    phoneNumber: '13800138000',
    displayName: '张三(已更新)',
    avatarUrl: 'https://example.com/new-avatar.jpg',
    createdAt: DateTime.parse('2023-01-01T00:00:00Z'),
    updatedAt: DateTime.parse('2023-01-03T00:00:00Z'),
  );

  group('getUserProfile', () {
    test('应当检查网络连接', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.getUserProfile(any))
          .thenAnswer((_) async => tUserModel);
      // act
      await repository.getUserProfile(tUserId);
      // assert
      verify(mockNetworkInfo.isConnected);
    });

    test('网络连接成功时，应当从远程数据源获取用户资料并返回成功结果', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.getUserProfile(any))
          .thenAnswer((_) async => tUserModel);
      // act
      final result = await repository.getUserProfile(tUserId);
      // assert
      verify(mockRemoteDataSource.getUserProfile(tUserId));
      expect(result, equals(Right(tUserModel)));
    });

    test('网络连接失败时，应当返回网络错误', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      // act
      final result = await repository.getUserProfile(tUserId);
      // assert
      verifyNever(mockRemoteDataSource.getUserProfile(any));
      
      expect(result.isLeft(), true);
      result.fold(
        (failure) => expect(failure, isA<NetworkFailure>()),
        (_) => fail('应该返回NetworkFailure'),
      );
    });

    test('远程数据源抛出服务器异常时，应当返回服务器错误', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.getUserProfile(any))
          .thenThrow(ServerException(message: '服务器错误', statusCode: 500));
      // act
      final result = await repository.getUserProfile(tUserId);
      // assert
      verify(mockRemoteDataSource.getUserProfile(tUserId));
      
      expect(result.isLeft(), true);
      result.fold(
        (failure) => expect(failure, isA<ServerFailure>()),
        (_) => fail('应该返回ServerFailure'),
      );
    });
  });

  group('updateUserProfile', () {
    final tProfileData = {
      'displayName': '张三(已更新)',
      'avatarUrl': 'https://example.com/new-avatar.jpg',
    };

    test('应当检查网络连接', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.updateUserProfile(any, any))
          .thenAnswer((_) async => tUpdatedUserModel);
      // act
      await repository.updateUserProfile(tUserId, tProfileData);
      // assert
      verify(mockNetworkInfo.isConnected);
    });

    test('网络连接成功时，应当通过远程数据源更新用户资料并返回成功结果', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.updateUserProfile(any, any))
          .thenAnswer((_) async => tUpdatedUserModel);
      // act
      final result = await repository.updateUserProfile(tUserId, tProfileData);
      // assert
      verify(mockRemoteDataSource.updateUserProfile(tUserId, tProfileData));
      expect(result, equals(Right(tUpdatedUserModel)));
    });

    test('网络连接失败时，应当返回网络错误', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      // act
      final result = await repository.updateUserProfile(tUserId, tProfileData);
      // assert
      verifyNever(mockRemoteDataSource.updateUserProfile(any, any));
      
      expect(result.isLeft(), true);
      result.fold(
        (failure) => expect(failure, isA<NetworkFailure>()),
        (_) => fail('应该返回NetworkFailure'),
      );
    });

    test('远程数据源抛出服务器异常时，应当返回服务器错误', () async {
      // arrange
      when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(mockRemoteDataSource.updateUserProfile(any, any))
          .thenThrow(ServerException(message: '服务器错误', statusCode: 500));
      // act
      final result = await repository.updateUserProfile(tUserId, tProfileData);
      // assert
      verify(mockRemoteDataSource.updateUserProfile(tUserId, tProfileData));
      
      expect(result.isLeft(), true);
      result.fold(
        (failure) => expect(failure, isA<ServerFailure>()),
        (_) => fail('应该返回ServerFailure'),
      );
    });
  });
} 