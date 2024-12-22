import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../data/models/chat_message.dart';
import '../../data/models/chat_conversation.dart';
import '../../services/ai_service.dart';
import '../../services/voice_service.dart';
import '../../core/config/doubao_config.dart';
import '../../data/database/database_helper.dart';
import '../../services/chat_service.dart';
import '../../services/doubao_service.dart';

class AiChatController extends GetxController {
  final ChatService _chatService = Get.find<ChatService>();
  final DouBaoService _douBaoService = Get.find<DouBaoService>();
  final AiService _aiService = Get.find();
  final VoiceService _voiceService = Get.find();
  
  late final ChatConversation conversation;
  final messages = <ChatMessage>[].obs;
  final isTyping = false.obs;
  final selectedModel = DouBaoConfig.defaultModel.obs;

  @override
  void onInit() {
    super.onInit();
    conversation = Get.arguments as ChatConversation;
    _loadMessages();
  }

  Future<void> _loadMessages() async {
    try {
      // TODO: 加载历史消息
    } catch (e) {
      print('Error loading messages: $e');
    }
  }

  Future<void> sendTextMessage(String text) async {
    try {
      isTyping.value = true;

      // 添加用户消息
      final userMessage = await _chatService.sendMessage(
        conversationId: conversation.id,
        content: text,
        senderId: ChatMessage.senderUser,
        senderAvatar: 'https://via.placeholder.com/100',
        messageType: ChatMessage.typeText,
      );
      messages.insert(0, userMessage);

      // 获取AI回复
      final response = await _chatService.getAiResponse(text, conversation.model);

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

  void startVoiceRecord() async {
    try {
      await _voiceService.startRecording();
    } catch (e) {
      print('Error starting voice record: $e');
    }
  }

  void stopVoiceRecord() async {
    try {
      final audioData = await _voiceService.stopRecording();
      if (audioData.isNotEmpty) {
        final message = ChatMessage(
          id: DateTime.now().toString(),
          conversationId: conversation.id,
          content: audioData,
          type: 'voice',
          senderId: 'user',
          senderAvatar: 'https://via.placeholder.com/100',
          createdAt: DateTime.now(),
          isRead: true,
        );
        messages.insert(0, message);
      }
    } catch (e) {
      print('Error stopping voice record: $e');
    }
  }

  void cancelVoiceRecord() async {
    try {
      await _voiceService.stopRecording();
    } catch (e) {
      print('Error canceling voice record: $e');
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
              Container(
                margin: const EdgeInsets.symmetric(vertical: 8),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
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

  void showAssistantSettings() {
    Get.toNamed('/settings/assistant');
  }

  void showVoiceSettings() {
    Get.toNamed('/settings/voice');
  }

  void showLanguageSettings() {
    Get.toNamed('/settings/language');
  }

  void pickImage() {
    Get.toNamed('/gallery');
  }

  void pickFile() {
    Get.toNamed('/files');
  }

  String _getAssistantType(String title) {
    switch (title) {
      case '小艾':
        return 'xiaoi';
      case '老克':
        return 'laoke';
      case '小克':
        return 'xiaoke';
      default:
        return 'xiaoi';
    }
  }

  void changeModel(String model) {
    selectedModel.value = model;
    // 更新会话模型
    conversation.model = model;
    _chatService.updateConversation(conversation);
    
    // 根据模型更新头像和标题
    switch (model) {
      case 'xiaoai':
        conversation.avatar = 'assets/images/xiaoai_avatar.png';
        conversation.title = '小艾';
        break;
      case 'laoke':
        conversation.avatar = 'assets/images/laoke_avatar.png';
        conversation.title = '老克';
        break;
      case 'xiaoke':
        conversation.avatar = 'assets/images/xiaoke_avatar.png';
        conversation.title = '小克';
        break;
    }
    update();
  }

  Future<void> updateConversationModel(int conversationId, String model) async {
    await DatabaseHelper().database.then((db) {
      return db.update(
        'conversations',
        {'model': model},
        where: 'id = ?',
        whereArgs: [conversationId],
      );
    });
  }
} 