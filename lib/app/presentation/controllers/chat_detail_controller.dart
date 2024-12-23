import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../data/models/chat_message.dart';
import '../../data/models/chat_conversation.dart';
import '../../services/chat_service.dart';
import '../../core/config/assistant_config.dart';

class ChatDetailController extends GetxController {
  final ChatService _chatService = Get.find();
  
  late final ChatConversation conversation;
  final messages = <ChatMessage>[].obs;
  final isTyping = false.obs;

  @override
  void onInit() {
    super.onInit();
    conversation = Get.arguments as ChatConversation? ?? ChatConversation(
      id: 1,
      title: '测试会话',
      model: 'xiaoai',
      avatar: AssistantConfig.xiaoai['avatar']!,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    _loadMessages();
  }

  Future<void> _loadMessages() async {
    try {
      final loadedMessages = await _chatService.getMessages(conversation.id);
      messages.assignAll(loadedMessages);
    } catch (e) {
      print('Error loading messages: $e');
    }
  }

  Future<void> sendMessage(String content) async {
    try {
      isTyping.value = true;

      // 添加用户消息
      final userMessage = ChatMessage(
        id: DateTime.now().toString(),
        conversationId: conversation.id,
        content: content,
        type: ChatMessage.typeText,
        senderId: ChatMessage.senderUser,
        senderAvatar: 'assets/images/default_avatar.png',
        createdAt: DateTime.now(),
        isRead: true,
      );
      messages.add(userMessage);

      // 获取AI回复
      final response = await _chatService.sendMessage(content, conversation.model);
      
      // 添加AI回复
      final aiMessage = ChatMessage(
        id: DateTime.now().toString(),
        conversationId: conversation.id,
        content: response,
        type: ChatMessage.typeText,
        senderId: ChatMessage.senderAi,
        senderAvatar: conversation.avatar,
        createdAt: DateTime.now(),
        isRead: true,
      );
      
      messages.add(aiMessage);
    } catch (e) {
      print('Error sending message: $e');
    } finally {
      isTyping.value = false;
    }
  }

  void onTapAvatar(String userId) {
    Get.toNamed('/profile/$userId');
  }

  void onLongPressMessage(ChatMessage message) {
    Get.bottomSheet(
      Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(20),
          ),
        ),
        child: SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.copy),
                title: const Text('复制'),
                onTap: () {
                  // TODO: 实现复制功能
                  Get.back();
                },
              ),
              ListTile(
                leading: const Icon(Icons.delete),
                title: const Text('删除'),
                onTap: () async {
                  await _chatService.deleteMessage(message.id);
                  messages.remove(message);
                  Get.back();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  void showSettings() {
    Get.toNamed('/settings/chat');
  }
} 