import 'package:injectable/injectable.dart';
import '../../../services/features/health/health_service.dart';

@injectable
class GetHealthMetricsUseCase {
  final HealthService _healthService;

  GetHealthMetricsUseCase(this._healthService);

  Future<Map<String, dynamic>> call() async {
    return _healthService.getHealthMetrics();
  }
} 