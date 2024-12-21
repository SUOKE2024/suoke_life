import 'package:get/get.dart';
import '../../data/models/ai_chat.dart';
import '../../services/ai_service.dart';

class AiChatController extends GetxController {
  final AiService _aiService = Get.find();
  final messages = <AiChat>[].obs;
  
  late final String assistantType;
  late final String assistantName;

  @override
  void onInit() {
    super.onInit();
    assistantType = Get.parameters['type'] ?? 'xiaoi';
    assistantName = _getAssistantName(assistantType);
    loadHistory();
  }

  String _getAssistantName(String type) {
    switch (type) {
      case 'xiaoi': return '小艾';
      case 'laoke': return '老克';
      case 'xiaoke': return '小克';
      default: return '助手';
    }
  }

  Future<void> loadHistory() async {
    // 加载历史消息
  }

  Future<void> sendMessage(String text) async {
    if (text.isEmpty) return;

    final message = AiChat(
      id: DateTime.now().toString(),
      userId: 'current_user',
      assistantType: assistantType,
      message: text,
      createdAt: DateTime.now(),
    );

    messages.insert(0, message);

    try {
      final response = await _aiService.chatWithAssistant(text, assistantType);
      
      final responseMessage = AiChat(
        id: DateTime.now().toString(),
        userId: assistantType,
        assistantType: assistantType,
        message: response,
        createdAt: DateTime.now(),
      );

      messages.insert(0, responseMessage);
    } catch (e) {
      Get.snackbar('错误', '发送消息失败');
    }
  }

  Future<void> startVoiceInput() async {
    // 实现语音输入
  }
} 