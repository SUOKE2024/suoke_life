import 'package:suoke_life/lib/core/services/network_service.dart';

class LLMServiceClient {
  final NetworkService _networkService;

  LLMServiceClient(this._networkService);

  Future<String> generateText(String prompt) async {
    final response = await _networkService.post('/llm/generate', {'prompt': prompt});
    if (response is Map && response.containsKey('response')) {
      return response['response'];
    } else {
      throw Exception('Invalid response format');
    }
  }
} 