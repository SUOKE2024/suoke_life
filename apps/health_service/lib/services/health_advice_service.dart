import 'package:injectable/injectable.dart';
import 'package:suoke_life/core/network/health_service_client.dart';

@injectable
class HealthAdviceService {
  final HealthServiceClient _healthServiceClient;

  HealthAdviceService(this._healthServiceClient);

  Future<String> getHealthAdvice(String userId) async {
    final response = await _healthServiceClient.getHealthData(userId);
    return 'Health advice based on: ${response.data}';
  }
} 