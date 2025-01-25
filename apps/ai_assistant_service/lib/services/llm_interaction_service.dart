import 'package:injectable/injectable.dart';
import 'package:suoke_life/core/network/llm_service_client.dart';

@injectable
class LLMInteractionService {
  final LLMServiceClient _llmServiceClient;

  LLMInteractionService(this._llmServiceClient);

  Future<String> generateResponse(String prompt) async {
    final response = await _llmServiceClient.generateText(prompt);
    return response.data.toString();
  }
} 