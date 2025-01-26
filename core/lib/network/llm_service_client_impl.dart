import 'package:core/network/llm_service_client.dart';
import 'package:backend/apps/llm_service/lib/models/request.dart';
import 'package:core/models/health_models.dart';

class LLMServiceClientImpl implements LLMServiceClient {
  const LLMServiceClientImpl();

  @override
  Future<List<HealthRisk>> analyzeHealthRisks(
      String medicalHistory, BiologicalSignals signals) async {
    try {
      final response = await _dio.post('$_baseUrl/analyze', data: {
        'medical_history': medicalHistory,
        'vital_signs': signals.toJson()
      });

      return (response.data['risks'] as List)
          .map((json) => HealthRisk.fromJson(json))
          .toList();
    } on DioException catch (e) {
      if (e.response?.statusCode == 503) {
        throw LLMServiceUnavailableException();
      }
      throw LLMServiceException(e.message ?? '未知错误');
    }
  }
}
