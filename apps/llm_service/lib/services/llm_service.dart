import 'package:injectable/injectable.dart';
import 'package:suoke_life/core/network/llm_service_client.dart';

@injectable
class LLMService {
  final LLMServiceClient _llmServiceClient;

  LLMService(this._llmServiceClient);

  Future<String> generateText(String prompt) async {
    final response = await _llmServiceClient.generateText(prompt);
    return 'LLM response: ${response.data}';
  }
} 