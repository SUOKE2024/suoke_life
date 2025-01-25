import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/domain/usecases/health/get_health_metrics_usecase.dart';
import 'package:suoke_app/app/services/features/health/health_service.dart';

class MockHealthService extends Mock implements HealthService {
  bool _shouldThrow = false;

  @override
  Future<Map<String, dynamic>> getHealthMetrics() async {
    if (_shouldThrow) {
      throw Exception('Failed to get metrics');
    }
    return {'steps': 1000, 'calories': 500};
  }

  void throwOnNextCall() {
    _shouldThrow = true;
  }
}

void main() {
  late GetHealthMetricsUseCase useCase;
  late MockHealthService mockHealthService;

  setUp(() {
    mockHealthService = MockHealthService();
    useCase = GetHealthMetricsUseCase(mockHealthService);
  });

  test('should get health metrics from service', () async {
    final metrics = {'steps': 1000, 'calories': 500};
    final result = await useCase();
    expect(result, metrics);
  });

  test('should throw error when service fails', () {
    mockHealthService.throwOnNextCall();
    expect(
      () => useCase(),
      throwsA(isA<Exception>()),
    );
  });
} 