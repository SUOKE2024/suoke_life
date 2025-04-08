import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/utils/secure_storage.dart';
import 'package:suoke_life/data/datasources/remote/auth_api_service.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:suoke_life/domain/usecases/auth_usecases.dart';
import 'package:suoke_life/presentation/auth/notifiers/auth_state.dart';
import 'package:suoke_life/presentation/auth/notifiers/auth_state_notifier.dart';
import 'biometric_auth_test.mocks.dart'; // 添加生成的mock类导入

// 生成Mock类
@GenerateMocks([AuthRepository, SecureStorage, AuthApiService])
void main() {
  late MockAuthRepository mockAuthRepository;
  late MockSecureStorage mockSecureStorage;
  late AuthStateNotifier authStateNotifier;

  setUp(() {
    mockAuthRepository = MockAuthRepository();
    mockSecureStorage = MockSecureStorage();
    authStateNotifier = AuthStateNotifier(
      authRepository: mockAuthRepository,
      secureStorage: mockSecureStorage,
    );
  });

  group('生物识别验证', () {
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
    final tAuthResult = AuthResult(
      user: tUser,
      token: tAuthToken,
    );

    test('生物识别验证成功时，应当更新认证状态为已认证', () async {
      // arrange
      when(mockAuthRepository.verifyBiometric(any, any))
          .thenAnswer((_) async => tAuthResult);

      // act
      await authStateNotifier.verifyBiometric('userId', 'biometricToken');

      // assert
      verify(mockAuthRepository.verifyBiometric('userId', 'biometricToken'));
      expect(authStateNotifier.state.user, equals(tUser));
      expect(authStateNotifier.state.authToken, equals(tAuthToken));
      expect(authStateNotifier.state.isAuthenticated, equals(true));
      expect(authStateNotifier.state.isLoading, equals(false));
      expect(authStateNotifier.state.error, equals(null));
    });

    test('生物识别验证失败时，应当更新认证状态为错误', () async {
      // arrange
      when(mockAuthRepository.verifyBiometric(any, any))
          .thenThrow(AuthenticationFailure(message: '生物识别认证失败'));

      // act
      await authStateNotifier.verifyBiometric('userId', 'biometricToken');

      // assert
      verify(mockAuthRepository.verifyBiometric('userId', 'biometricToken'));
      expect(authStateNotifier.state.isAuthenticated, equals(false));
      expect(authStateNotifier.state.isLoading, equals(false));
      expect(authStateNotifier.state.error, equals('生物识别认证失败'));
    });

    test('生物识别验证过程中应当更新状态为加载中', () async {
      // arrange
      when(mockAuthRepository.verifyBiometric(any, any))
          .thenAnswer((_) async {
            // 验证在异步操作完成前状态是否为加载中
            expect(authStateNotifier.state.isLoading, equals(true));
            return tAuthResult;
          });

      // act
      await authStateNotifier.verifyBiometric('userId', 'biometricToken');

      // assert
      verify(mockAuthRepository.verifyBiometric('userId', 'biometricToken'));
      expect(authStateNotifier.state.isLoading, equals(false));
    });
  });

  group('生物识别注册', () {
    test('生物识别注册成功时，应当返回成功状态', () async {
      // arrange
      when(mockAuthRepository.registerBiometric(any, any))
          .thenAnswer((_) async => true);

      // act
      await authStateNotifier.registerBiometric('userId', 'fingerprintAuth');

      // assert
      verify(mockAuthRepository.registerBiometric('userId', 'fingerprintAuth'));
      expect(authStateNotifier.state.isLoading, equals(false));
      expect(authStateNotifier.state.error, equals(null));
    });

    test('生物识别注册失败时，应当更新状态为错误', () async {
      // arrange
      when(mockAuthRepository.registerBiometric(any, any))
          .thenAnswer((_) async => false);

      // act
      await authStateNotifier.registerBiometric('userId', 'fingerprintAuth');

      // assert
      verify(mockAuthRepository.registerBiometric('userId', 'fingerprintAuth'));
      expect(authStateNotifier.state.isLoading, equals(false));
      expect(authStateNotifier.state.error, equals('生物识别注册失败'));
    });
  });
} 