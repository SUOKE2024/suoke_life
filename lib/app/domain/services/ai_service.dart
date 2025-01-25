import '../base_service.dart';

abstract class AIService extends BaseService {
  Future<String> sendMessage(String message);
} 