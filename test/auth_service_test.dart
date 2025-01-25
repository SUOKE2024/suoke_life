import 'package:core/core.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:auth/auth.dart';
import 'package:core/network/network_service.dart';

// 移除不必要的导入
// import 'auth_service_test.mocks.dart';

import 'package:suoke_life_app_app_app/test/helpers/mock_generation.mocks.dart';

void main() {
  late AuthService authService;
  late MockNetworkService mockNetworkService;
  late MockLocalStorageService mockLocalStorageService;

  setUp(() {
    mockNetworkService = MockNetworkService();
    mockLocalStorageService = MockLocalStorageService();
    authService = AuthService(mockNetworkService, mockLocalStorageService);
  });

  group('AuthService', () {
    test('login should return true on successful login', () async {
      // Arrange
      const email = 'test@example.com';
      const password = 'password';
      const token = 'token';

      when(mockNetworkService.post(any, data: anyNamed('data')))
          .thenAnswer((_) async => Response(
                data: {'token': token},
                statusCode: 200,
                requestOptions: RequestOptions(path: ''),
              ));

      when(mockLocalStorageService.save(any, any)).thenAnswer((_) async {});

      // Act
      final result = await authService.login(
        email: email,
        password: password,
      );

      // Assert
      expect(result, true);
      verify(mockLocalStorageService.save('token', token)).called(1);
    });

    test('login should return false on failed login', () async {
      // Arrange
      const email = 'test@example.com';
      const password = 'password';

      when(mockNetworkService.post(any, data: anyNamed('data')))
          .thenAnswer((_) async => Response(
                data: {'message': 'Invalid credentials'},
                statusCode: 401,
                requestOptions: RequestOptions(path: ''),
              ));

      // Act
      final result = await authService.login(
        email: email,
        password: password,
      );

      // Assert
      expect(result, false);
      verifyNever(mockLocalStorageService.save(any, any));
    });

    test('login with email and password successfully', () async {
      // Arrange
      const email = 'test@example.com';
      const password = 'password';
      const token = 'token';
      const user = {'id': '1', 'email': 'test@example.com'};

      when(mockNetworkService.post('/login', data: {'email': email, 'password': password}))
          .thenAnswer((_) async => Response(
                requestOptions: RequestOptions(path: '/login'),
                data: {'token': token, 'user': user},
                statusCode: 200,
              ));
      when(mockLocalStorageService.save('token', token)).thenAnswer((_) async {});
      when(mockLocalStorageService.saveMap('user', user)).thenAnswer((_) async {});

      // Act
      final result = await authService.login(email: email, password: password);

      // Assert
      expect(result, true);
      verify(mockNetworkService.post('/login', data: {'email': email, 'password': password})).called(1);
      verify(mockLocalStorageService.save('token', token)).called(1);
      verify(mockLocalStorageService.saveMap('user', user)).called(1);
    });

    test('register successfully', () async {
      // Arrange
      const phoneNumber = '1234567890';
      const verificationCode = '123456';
      const password = 'password';
      const token = 'token';
      const user = {'id': '1', 'phoneNumber': phoneNumber};

      when(mockNetworkService.post('/register',
              data: {'phoneNumber': phoneNumber, 'verificationCode': verificationCode, 'password': password}))
          .thenAnswer((_) async => Response(
                requestOptions: RequestOptions(path: '/register'),
                data: {},
                statusCode: 200,
              ));
      when(mockNetworkService.post('/login', data: {'phoneNumber': phoneNumber}))
          .thenAnswer((_) async => Response(
                requestOptions: RequestOptions(path: '/login'),
                data: {'token': token, 'user': user},
                statusCode: 200,
              ));
      when(mockLocalStorageService.save('token', token)).thenAnswer((_) async {});
      when(mockLocalStorageService.saveMap('user', user)).thenAnswer((_) async {});

      // Act
      await authService.register(phoneNumber: phoneNumber, verificationCode: verificationCode, password: password);

      // Assert
      verify(mockNetworkService.post('/register',
              data: {'phoneNumber': phoneNumber, 'verificationCode': verificationCode, 'password': password}))
          .called(1);
      verify(mockNetworkService.post('/login', data: {'phoneNumber': phoneNumber})).called(1);
      verify(mockLocalStorageService.save('token', token)).called(1);
      verify(mockLocalStorageService.saveMap('user', user)).called(1);
    });

    test('logout successfully', () async {
      // Arrange
      when(mockLocalStorageService.remove('token')).thenAnswer((_) async {});
      when(mockLocalStorageService.remove('user')).thenAnswer((_) async {});

      // Act
      await authService.logout();

      // Assert
      verify(mockLocalStorageService.remove('token')).called(1);
      verify(mockLocalStorageService.remove('user')).called(1);
    });
  });
}
