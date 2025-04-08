import 'package:dartz/dartz.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/usecases/update_user_profile.dart';
import 'package:suoke_life/presentation/profile/controllers/user_profile_controller.dart';

import 'user_profile_controller_test.mocks.dart';

@GenerateMocks([UpdateUserProfile])
void main() {
  late UserProfileController controller;
  late MockUpdateUserProfile mockUpdateUserProfile;
  late ProviderContainer container;

  setUp(() {
    mockUpdateUserProfile = MockUpdateUserProfile();
    controller = UserProfileController(
      updateUserProfileUseCase: mockUpdateUserProfile,
    );
    container = ProviderContainer(
      overrides: [
        userProfileControllerProvider.overrideWith(
          (ref) => controller,
        ),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('初始状态', () {
    test('初始状态应为UserProfileInitial', () {
      // assert
      expect(controller.state, isA<UserProfileInitial>());
    });
  });

  group('updateProfile', () {
    final userId = '123456';
    final profileData = {
      'displayName': '测试用户',
    };
    final updatedUser = User(
      id: userId,
      username: 'testuser',
      email: 'test@example.com',
      phoneNumber: '13800138000',
      displayName: '测试用户',
      avatarUrl: 'https://example.com/avatar.png',
      createdAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
      updatedAt: DateTime.parse('2023-01-02T00:00:00.000Z'),
    );

    test('成功更新用户资料时应该设置成功状态', () async {
      // arrange
      when(mockUpdateUserProfile(any))
          .thenAnswer((_) async => Right(updatedUser));

      // act
      await controller.updateProfile(
        userId: userId, 
        profileData: profileData,
      );

      // assert
      verify(mockUpdateUserProfile(UpdateUserProfileParams(
        userId: userId,
        profileData: profileData,
      )));
      expect(container.read(userProfileControllerProvider), isA<UserProfileSuccess>());
      expect(
        (container.read(userProfileControllerProvider) as UserProfileSuccess).user,
        equals(updatedUser),
      );
    });

    test('更新失败时应该设置错误状态', () async {
      // arrange
      when(mockUpdateUserProfile(any))
          .thenAnswer((_) async => Left(ServerFailure(message: '服务器错误')));

      // act
      await controller.updateProfile(
        userId: userId, 
        profileData: profileData,
      );

      // assert
      verify(mockUpdateUserProfile(UpdateUserProfileParams(
        userId: userId,
        profileData: profileData,
      )));
      expect(container.read(userProfileControllerProvider), isA<UserProfileError>());
      expect(
        (container.read(userProfileControllerProvider) as UserProfileError).message,
        equals('服务器错误'),
      );
    });

    test('网络错误时应该设置特定的错误消息', () async {
      // arrange
      when(mockUpdateUserProfile(any))
          .thenAnswer((_) async => Left(NetworkFailure(message: '无网络连接')));

      // act
      await controller.updateProfile(
        userId: userId, 
        profileData: profileData,
      );

      // assert
      verify(mockUpdateUserProfile(UpdateUserProfileParams(
        userId: userId,
        profileData: profileData,
      )));
      expect(container.read(userProfileControllerProvider), isA<UserProfileError>());
      expect(
        (container.read(userProfileControllerProvider) as UserProfileError).message,
        equals('无网络连接'),
      );
    });

    test('状态应该从加载状态开始', () async {
      // arrange
      when(mockUpdateUserProfile(any))
          .thenAnswer((_) async => Right(updatedUser));

      // act
      final future = controller.updateProfile(
        userId: userId, 
        profileData: profileData,
      );

      // assert - 在future完成之前检查状态
      expect(container.read(userProfileControllerProvider), isA<UserProfileLoading>());

      // 等待future完成
      await future;
    });
  });
} 