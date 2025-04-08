import 'package:flutter_test/flutter_test.dart';
import 'package:dartz/dartz.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/domain/entities/user_preferences.dart';
import 'package:suoke_life/domain/usecases/get_user_preferences.dart';
import 'package:suoke_life/domain/usecases/update_user_preferences.dart';

import 'mocks.mocks.dart';

void main() {
  late GetUserPreferences getUserPreferences;
  late UpdateUserPreferences updateUserPreferences;
  late MockUserRepository mockUserRepository;

  setUp(() {
    mockUserRepository = MockUserRepository();
    getUserPreferences = GetUserPreferences(repository: mockUserRepository);
    updateUserPreferences = UpdateUserPreferences(repository: mockUserRepository);
  });

  const tUserId = 'user123';
  final tUserPreferences = UserPreferences(
    userId: tUserId,
    themeMode: 'dark',
    language: 'zh',
    notificationsEnabled: true,
    dataCollectionConsent: true,
    createdAt: DateTime.parse('2023-01-01T00:00:00Z'),
    updatedAt: DateTime.parse('2023-01-01T00:00:00Z'),
  );

  group('GetUserPreferences', () {
    test('应当从用户仓库获取用户偏好设置', () async {
      // arrange
      when(mockUserRepository.getUserPreferences(any))
          .thenAnswer((_) async => Right(tUserPreferences));

      // act
      final result = await getUserPreferences(Params(userId: tUserId));

      // assert
      verify(mockUserRepository.getUserPreferences(tUserId));
      expect(result, Right(tUserPreferences));
    });

    test('应当将仓库返回的失败传递给调用方', () async {
      // arrange
      final failure = ServerFailure(message: '获取偏好设置失败');
      when(mockUserRepository.getUserPreferences(any))
          .thenAnswer((_) async => Left(failure));

      // act
      final result = await getUserPreferences(Params(userId: tUserId));

      // assert
      verify(mockUserRepository.getUserPreferences(tUserId));
      expect(result, Left(failure));
    });
  });

  group('UpdateUserPreferences', () {
    final tUpdatedPreferences = UserPreferences(
      userId: tUserId,
      themeMode: 'light',
      language: 'en',
      notificationsEnabled: false,
      dataCollectionConsent: true,
      createdAt: DateTime.parse('2023-01-01T00:00:00Z'),
      updatedAt: DateTime.parse('2023-01-02T00:00:00Z'),
    );

    final tPreferencesData = {
      'themeMode': 'light',
      'language': 'en',
      'notificationsEnabled': false,
    };

    test('应当通过用户仓库更新用户偏好设置', () async {
      // arrange
      when(mockUserRepository.updateUserPreferences(any, any))
          .thenAnswer((_) async => Right(tUpdatedPreferences));

      // act
      final result = await updateUserPreferences(
        UpdateUserPreferencesParams(
          userId: tUserId,
          preferences: tPreferencesData,
        ),
      );

      // assert
      verify(mockUserRepository.updateUserPreferences(tUserId, tPreferencesData));
      expect(result, Right(tUpdatedPreferences));
    });

    test('应当将仓库返回的失败传递给调用方', () async {
      // arrange
      final failure = ServerFailure(message: '更新偏好设置失败');
      when(mockUserRepository.updateUserPreferences(any, any))
          .thenAnswer((_) async => Left(failure));

      // act
      final result = await updateUserPreferences(
        UpdateUserPreferencesParams(
          userId: tUserId,
          preferences: tPreferencesData,
        ),
      );

      // assert
      verify(mockUserRepository.updateUserPreferences(tUserId, tPreferencesData));
      expect(result, Left(failure));
    });
  });
} 