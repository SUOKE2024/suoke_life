import 'package:get/get.dart';
import '../../../models/message.dart';
import '../../../services/ai/ai_service.dart';
import '../../../services/storage/chat_storage_service.dart';

class AIChatDetailController extends GetxController {
  final AIService _aiService;
  final ChatStorageService _storageService;
  
  final messages = <Message>[].obs;
  final isLoading = false.obs;
  final chatTitle = ''.obs;

  AIChatDetailController(this._aiService, this._storageService);

  @override
  void onInit() {
    super.onInit();
    chatTitle.value = Get.parameters['title'] ?? 'AI对话';
    loadMessages();
  }

  Future<void> loadMessages() async {
    try {
      isLoading.value = true;
      final chatId = Get.parameters['id'];
      if (chatId != null) {
        final history = await _storageService.getMessages(chatId);
        messages.value = history;
      }
    } catch (e) {
      Get.snackbar('错误', '加载消息失败: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> sendMessage(String text) async {
    if (text.isEmpty) return;

    try {
      // 添加用户消息
      final userMessage = Message(
        id: DateTime.now().toString(),
        type: MessageType.text,
        content: text,
        isFromUser: true,
        timestamp: DateTime.now(),
      );
      messages.insert(0, userMessage);
      await _storageService.saveMessage(userMessage);

      // 获取AI回复
      final response = await _aiService.chat(text);
      
      // 添加AI消息
      final aiMessage = Message(
        id: DateTime.now().toString(),
        type: MessageType.text,
        content: response,
        isFromUser: false,
        timestamp: DateTime.now(),
      );
      messages.insert(0, aiMessage);
      await _storageService.saveMessage(aiMessage);
      
    } catch (e) {
      Get.snackbar('错误', '发送消息失败: $e');
    }
  }

  Future<void> sendVoiceMessage(String path) async {
    // 实现语音消息发送逻辑
  }

  void showChatInfo() {
    // 显示对话信息
    Get.dialog(
      AlertDialog(
        title: Text('对话信息'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('消息数量: ${messages.length}'),
            Text('创建时间: ${messages.lastOrNull?.timestamp ?? "未知"}'),
          ],
        ),
        actions: [
          TextButton(
            child: Text('关闭'),
            onPressed: () => Get.back(),
          ),
        ],
      ),
    );
  }
} 