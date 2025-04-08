import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:suoke_life/domain/usecases/auth_usecases.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';

import 'user_repository_test.dart' as user_repository;
import 'user_preferences_test.dart' as user_preferences;
import 'user_remote_data_source_test.dart' as user_remote_data_source;
import 'user_profile_controller_test.dart' as user_profile_controller;

@GenerateMocks([AuthRepository])
void main() {
  group('用户仓库测试', () {
    user_repository.main();
  });

  group('用户偏好设置测试', () {
    user_preferences.main();
  });

  group('用户远程数据源测试', () {
    user_remote_data_source.main();
  });

  group('用户资料控制器测试', () {
    user_profile_controller.main();
  });
  
  group('认证用例测试', () {
    late AuthUseCases authUseCases;
    late MockAuthRepository mockAuthRepository;
    
    setUp(() {
      mockAuthRepository = MockAuthRepository();
      authUseCases = AuthUseCases(repository: mockAuthRepository);
    });
    
    group('login', () {
      final tEmail = 'test@example.com';
      final tPassword = 'password123';
      final tUser = User(
        id: 'user_123',
        username: 'testuser',
        email: tEmail,
        displayName: '测试用户',
        avatarUrl: 'https://example.com/avatar.png',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      final tAuthToken = AuthToken(
        accessToken: 'access_token',
        refreshToken: 'refresh_token',
        expiresIn: 3600,
      );
      
      test('登录成功时应当返回用户和令牌', () async {
        // arrange
        when(mockAuthRepository.login(any, any))
            .thenAnswer((_) async => Right((tUser, tAuthToken)));
        
        // act
        final result = await authUseCases.login(tEmail, tPassword);
        
        // assert
        verify(mockAuthRepository.login(tEmail, tPassword));
        expect(result, equals(Right((tUser, tAuthToken))));
      });
      
      test('登录失败时应当返回失败信息', () async {
        // arrange
        final tFailure = ServerFailure(message: '登录失败');
        when(mockAuthRepository.login(any, any))
            .thenAnswer((_) async => Left(tFailure));
        
        // act
        final result = await authUseCases.login(tEmail, tPassword);
        
        // assert
        verify(mockAuthRepository.login(tEmail, tPassword));
        expect(result, equals(Left(tFailure)));
      });
    });
    
    group('loginWithPhone', () {
      final tPhoneNumber = '13800138000';
      final tVerificationCode = '123456';
      final tUser = User(
        id: 'user_123',
        username: 'phoneuser',
        phoneNumber: tPhoneNumber,
        displayName: '手机用户',
        avatarUrl: 'https://example.com/avatar.png',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
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
      
      test('手机号登录成功时应当返回认证结果', () async {
        // arrange
        when(mockAuthRepository.loginWithPhone(any, any))
            .thenAnswer((_) async => tAuthResult);
        
        // act
        final result = await authUseCases.loginWithPhone(tPhoneNumber, tVerificationCode);
        
        // assert
        verify(mockAuthRepository.loginWithPhone(tPhoneNumber, tVerificationCode));
        expect(result, equals(tAuthResult));
        expect(result.user.phoneNumber, equals(tPhoneNumber));
      });
    });
    
    group('register', () {
      final tUserData = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'displayName': '新用户',
      };
      final tUser = User(
        id: 'user_789',
        username: 'newuser',
        email: 'new@example.com',
        displayName: '新用户',
        avatarUrl: 'https://example.com/default-avatar.png',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      final tAuthToken = AuthToken(
        accessToken: 'new_access_token',
        refreshToken: 'new_refresh_token',
        expiresIn: 3600,
      );
      
      test('注册成功时应当返回新用户和令牌', () async {
        // arrange
        when(mockAuthRepository.register(any))
            .thenAnswer((_) async => Right((tUser, tAuthToken)));
        
        // act
        final result = await authUseCases.register(tUserData);
        
        // assert
        verify(mockAuthRepository.register(tUserData));
        expect(result, equals(Right((tUser, tAuthToken))));
      });
    });
    
    group('refreshToken', () {
      final tRefreshToken = 'refresh_token';
      final tAuthToken = AuthToken(
        accessToken: 'new_access_token',
        refreshToken: 'new_refresh_token',
        expiresIn: 3600,
      );
      
      test('刷新令牌成功时应当返回新令牌', () async {
        // arrange
        when(mockAuthRepository.refreshToken(any))
            .thenAnswer((_) async => Right(tAuthToken));
        
        // act
        final result = await authUseCases.refreshToken(tRefreshToken);
        
        // assert
        verify(mockAuthRepository.refreshToken(tRefreshToken));
        expect(result, equals(Right(tAuthToken)));
      });
    });
    
    group('logout', () {
      test('登出成功时应当返回true', () async {
        // arrange
        when(mockAuthRepository.logout())
            .thenAnswer((_) async => const Right(true));
        
        // act
        final result = await authUseCases.logout();
        
        // assert
        verify(mockAuthRepository.logout());
        expect(result, equals(const Right(true)));
      });
    });
  });
} 