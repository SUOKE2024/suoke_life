import 'package:suoke_life/core/services/health_service.dart';

class HealthServiceImpl implements HealthService {
  @override
  Future<String> getHealthAdvice(String query) async {
    // TODO: Implement health advice logic
    return 'This is health advice for: $query';
  }
} 