import 'package:get/get.dart';
import '../../data/models/chat_message.dart';
import '../../data/models/chat_conversation.dart';
import '../../services/chat_service.dart';
import '../../services/ai/ai_service.dart';
import '../../core/config/assistant_config.dart';

class AssistantChatController extends GetxController {
  final ChatService _chatService = Get.find();
  final AiService _aiService = Get.find();
  
  final messages = <ChatMessage>[].obs;
  final isTyping = false.obs;
  final conversation = Rx<ChatConversation?>(null);
  
  @override
  void onInit() {
    super.onInit();
    final String? conversationId = Get.parameters['id'];
    if (conversationId != null) {
      loadConversation(conversationId);
    }
  }

  Future<void> loadConversation(String conversationId) async {
    try {
      final conv = await _chatService.getConversation(conversationId);
      conversation.value = conv;
      
      final history = await _chatService.getMessages(conversationId);
      messages.assignAll(history);
    } catch (e) {
      Get.snackbar('错误', '加载对话失败');
    }
  }

  Future<void> sendMessage(String content) async {
    if (content.isEmpty || conversation.value == null) return;

    try {
      isTyping.value = true;
      
      // 添加用户消息
      final userMessage = ChatMessage(
        id: DateTime.now().toString(),
        conversationId: conversation.value!.id,
        content: content,
        type: 'text',
        senderId: 'user',
        senderAvatar: 'assets/images/default_avatar.png',
        createdAt: DateTime.now(),
        isRead: true,
      );
      messages.add(userMessage);

      // 获取AI回复
      final response = await _aiService.chat(
        conversation.value!.model,
        content,
      );

      // 添加AI回复消息
      final aiMessage = ChatMessage(
        id: DateTime.now().toString(),
        conversationId: conversation.value!.id,
        content: response,
        type: 'text',
        senderId: 'assistant',
        senderAvatar: AssistantConfig.getAvatar(conversation.value!.model),
        createdAt: DateTime.now(),
        isRead: true,
      );
      messages.add(aiMessage);

      // 保存消息
      await _chatService.saveMessages([userMessage, aiMessage]);
      
    } catch (e) {
      Get.snackbar('错误', '发送消息失败');
    } finally {
      isTyping.value = false;
    }
  }

  void onTapAvatar() {
    if (conversation.value == null) return;
    Get.toNamed(
      '/assistant/profile/${conversation.value!.model}',
      arguments: conversation.value,
    );
  }

  void showSettings() {
    Get.toNamed('/settings/chat');
  }
} 