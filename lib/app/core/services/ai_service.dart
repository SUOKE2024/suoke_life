import 'package:get/get.dart';
import '../network/doubao_client.dart';
import '../../data/models/ai_chat.dart';

class AIService extends GetxService {
  final DoubaoClient _doubaoClient;
  
  AIService({required DoubaoClient doubaoClient}) : _doubaoClient = doubaoClient;

  Future<AIChat> chatWithXiaoAi(String message) async {
    try {
      final response = await _doubaoClient.chat(
        message,
        context: {'assistant': 'xiaoi', 'role': 'life_assistant'},
      );
      return AIChat.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }

  // 老克助手 - 知识顾问
  Future<AIChat> chatWithLaoKe(String message) async {
    try {
      final response = await _doubaoClient.chat(
        message,
        context: {'assistant': 'laoke', 'role': 'knowledge_advisor'},
      );
      return AIChat.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }

  // 小克助手 - 商务助手
  Future<AIChat> chatWithXiaoKe(String message) async {
    try {
      final response = await _doubaoClient.chat(
        message,
        context: {'assistant': 'xiaoke', 'role': 'business_assistant'},
      );
      return AIChat.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }
} 