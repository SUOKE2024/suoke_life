import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/domain/usecases/health/get_health_metrics_usecase.dart';
import 'package:suoke_app/app/domain/repositories/health_repository.dart';
import 'package:suoke_app/app/core/cache/cache_manager.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';

import 'get_health_metrics_test.mocks.dart';

@GenerateMocks([HealthRepository, CacheManager])
void main() {
  late MockSuokeService mockSuokeService;
  late GetHealthMetricsUseCase useCase;

  setUp(() {
    mockSuokeService = MockSuokeService();
    useCase = GetHealthMetricsUseCase(mockSuokeService);
  });

  group('GetHealthMetricsUseCase', () {
    test('should return health metrics when successful', () async {
      // Arrange
      final expectedMetrics = {'heart_rate': 75, 'steps': 8000};
      when(mockSuokeService.getUserProfile())
          .thenAnswer((_) async => expectedMetrics);

      // Act
      final result = await useCase.execute();

      // Assert
      expect(result, equals(expectedMetrics));
      verify(mockSuokeService.getUserProfile()).called(1);
    });

    test('should handle errors appropriately', () async {
      // Arrange
      when(mockSuokeService.getUserProfile())
          .thenThrow(Exception('Failed to get metrics'));

      // Act & Assert
      expect(
        () => useCase.execute(),
        throwsA(isA<Exception>()),
      );
    });
  });
} 