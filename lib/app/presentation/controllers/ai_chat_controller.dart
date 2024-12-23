import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../data/models/chat_message.dart';
import '../../data/models/chat_conversation.dart';
import '../../services/chat_service.dart';
import '../../core/config/assistant_config.dart';

class AiChatController extends GetxController {
  final ChatService _chatService = Get.find();
  
  final messages = <ChatMessage>[].obs;
  final isTyping = false.obs;
  final selectedModel = 'xiaoai'.obs;
  
  late final ChatConversation conversation;

  @override
  void onInit() {
    super.onInit();
    conversation = ChatConversation(
      id: DateTime.now().millisecondsSinceEpoch,
      title: 'AI助手',
      model: selectedModel.value,
      avatar: AssistantConfig.xiaoai['avatar']!,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
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
      final response = await _chatService.sendMessage(content, selectedModel.value);
      
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
                onTap: () {
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

  void onTapAvatar(String userId) {
    // TODO: 实现头像点击功能
  }

  void changeModel(String model) {
    selectedModel.value = model;
    conversation = conversation.copyWith(
      model: model,
      avatar: AssistantConfig.xiaoai['avatar']!,
    );
  }

  void showSettings() {
    Get.toNamed('/settings/ai');
  }

  void startVoiceInput() {
    // TODO: 实现语音输入开始
  }

  void stopVoiceInput() {
    // TODO: 实现语音输入结束
  }

  void cancelVoiceInput() {
    // TODO: 实现语音输入取消
  }

  void showExtraOptions() {
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
                leading: const Icon(Icons.image),
                title: const Text('图片'),
                onTap: () {
                  // TODO: 实现图片功能
                  Get.back();
                },
              ),
              ListTile(
                leading: const Icon(Icons.file_present),
                title: const Text('文件'),
                onTap: () {
                  // TODO: 实现文件功能
                  Get.back();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
} 