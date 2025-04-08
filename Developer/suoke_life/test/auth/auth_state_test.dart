import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:suoke_life/domain/entities/user.dart';
import 'package:suoke_life/presentation/auth/notifiers/auth_state.dart';

void main() {
  group('AuthState', () {
    test('初始状态应当设置为未认证', () {
      final initialState = AuthState.initial();
      
      expect(initialState.isAuthenticated, false);
      expect(initialState.isLoading, false);
      expect(initialState.user, null);
      expect(initialState.authToken, null);
      expect(initialState.error, null);
    });
    
    test('加载状态应当设置isLoading为true', () {
      final initialState = AuthState.initial();
      final loadingState = initialState.copyWith(isLoading: true);
      
      expect(loadingState.isLoading, true);
      expect(loadingState.isAuthenticated, false);
    });
    
    test('认证状态应当包含用户信息和令牌', () {
      final user = User(
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
      
      final token = AuthToken(
        accessToken: 'access_token',
        refreshToken: 'refresh_token',
        expiresIn: 3600,
      );
      
      final initialState = AuthState.initial();
      final authenticatedState = initialState.copyWith(
        isAuthenticated: true,
        user: user,
        authToken: token,
      );
      
      expect(authenticatedState.isAuthenticated, true);
      expect(authenticatedState.user, user);
      expect(authenticatedState.authToken, token);
      expect(authenticatedState.error, null);
    });
    
    test('错误状态应当包含错误信息', () {
      final initialState = AuthState.initial();
      final errorState = initialState.copyWith(
        error: '认证失败',
        isLoading: false,
      );
      
      expect(errorState.error, '认证失败');
      expect(errorState.isLoading, false);
      expect(errorState.isAuthenticated, false);
    });
    
    test('退出登录状态应当重置为初始状态', () {
      final user = User(
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
      
      final token = AuthToken(
        accessToken: 'access_token',
        refreshToken: 'refresh_token',
        expiresIn: 3600,
      );
      
      final authenticatedState = AuthState(
        isAuthenticated: true,
        isLoading: false,
        user: user,
        authToken: token,
        error: null,
      );
      
      final loggedOutState = authenticatedState.copyWith(
        isAuthenticated: false,
        user: null,
        authToken: null,
      );
      
      expect(loggedOutState.isAuthenticated, false);
      expect(loggedOutState.user, null);
      expect(loggedOutState.authToken, null);
      expect(loggedOutState.isLoading, false);
    });
  });
} 