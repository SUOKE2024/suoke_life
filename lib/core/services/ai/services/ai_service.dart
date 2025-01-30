import 'package:injectable/injectable.dart';
import '../models/ai_service_response.dart';
import 'ai_service_client.dart';

@injectable
class AIService {
  final AIServiceClient _client;
  
  AIService(this._client);

  Future<AIServiceResponse> chat(String message) async {
    try {
      return await _client.chat({
        'message': message,
        'timestamp': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      rethrow;
    }
  }
} 