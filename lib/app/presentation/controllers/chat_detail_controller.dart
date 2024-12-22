import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../data/models/chat_message.dart';
import '../../data/models/chat_conversation.dart';
import '../../services/chat_service.dart';

class ChatDetailController extends GetxController {
  final ChatService _chatService = Get.find();
  
  late final ChatConversation conversation;
  final messages = <ChatMessage>[].obs;
  final isTyping = false.obs;

  @override
  void onInit() {
    super.onInit();
    conversation = Get.arguments as ChatConversation;
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

      // 发送用户消息
      final userMessage = await _chatService.sendMessage(
        conversationId: conversation.id,
        content: content,
        senderId: ChatMessage.senderUser,
        senderAvatar: 'https://via.placeholder.com/100',
        messageType: ChatMessage.typeText,
      );
      messages.insert(0, userMessage);

      // 获取AI回复
      final response = await _chatService.getAiResponse(content, conversation.model);

      // 添加AI回复
      final aiMessage = await _chatService.sendMessage(
        conversationId: conversation.id,
        content: response,
        senderId: ChatMessage.senderAi,
        senderAvatar: conversation.avatar,
        messageType: ChatMessage.typeText,
      );
      messages.insert(0, aiMessage);
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