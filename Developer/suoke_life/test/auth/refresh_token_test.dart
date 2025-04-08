import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/domain/entities/auth_token.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:suoke_life/domain/usecases/refresh_token.dart';

import 'refresh_token_test.mocks.dart';

@GenerateMocks([AuthRepository])
void main() {
  late RefreshToken usecase;
  late MockAuthRepository mockAuthRepository;

  setUp(() {
    mockAuthRepository = MockAuthRepository();
    usecase = RefreshToken(repository: mockAuthRepository);
  });

  final tRefreshToken = 'refresh_token';
  final tAuthToken = AuthToken(
    accessToken: 'new_access_token',
    refreshToken: 'new_refresh_token',
    expiresIn: 3600,
  );

  test('应当从认证存储库获取新的认证令牌', () async {
    // arrange
    when(mockAuthRepository.refreshToken(any))
        .thenAnswer((_) async => Right(tAuthToken));

    // act
    final result = await usecase(RefreshTokenParams(refreshToken: tRefreshToken));

    // assert
    expect(result, Right(tAuthToken));
    verify(mockAuthRepository.refreshToken(tRefreshToken));
    verifyNoMoreInteractions(mockAuthRepository);
  });

  test('应当返回存储库返回的失败', () async {
    // arrange
    final failure = ServerFailure(message: '令牌刷新失败');
    when(mockAuthRepository.refreshToken(any))
        .thenAnswer((_) async => Left(failure));

    // act
    final result = await usecase(RefreshTokenParams(refreshToken: tRefreshToken));

    // assert
    expect(result, Left(failure));
    verify(mockAuthRepository.refreshToken(tRefreshToken));
    verifyNoMoreInteractions(mockAuthRepository);
  });
} 