import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../data/models/chat.dart';
import '../../data/models/message.dart';
import '../../services/chat_service.dart';
import '../../core/base/base_controller.dart';

class ChatDetailController extends BaseController {
  final _chatService = Get.find<ChatService>();
  
  final chat = Rxn<Chat>();
  final messages = <Message>[].obs;
  final isLoading = false.obs;
  final hasMore = true.obs;
  
  final inputController = TextEditingController();
  String? _lastMessageId;

  @override
  void onInit() {
    super.onInit();
    final chatId = Get.parameters['id'];
    if (chatId != null) {
      loadChat(chatId);
      loadMessages(chatId);
    }
  }

  @override
  void onClose() {
    inputController.dispose();
    super.onClose();
  }

  Future<void> loadChat(String chatId) async {
    try {
      final result = await _chatService.getChat(chatId);
      chat.value = result;
    } catch (e) {
      showError('加载聊天信息失败');
    }
  }

  Future<void> loadMessages(String chatId) async {
    if (isLoading.value || !hasMore.value) return;
    
    try {
      isLoading.value = true;
      final result = await _chatService.getMessages(
        chatId,
        limit: 20,
        before: _lastMessageId,
      );
      
      if (result.isEmpty) {
        hasMore.value = false;
      } else {
        messages.addAll(result);
        _lastMessageId = result.last.id;
      }
    } catch (e) {
      showError('加载消息失败');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> loadMoreMessages() async {
    if (chat.value != null) {
      await loadMessages(chat.value!.id);
    }
  }

  Future<void> sendTextMessage(String text) async {
    if (text.isEmpty || chat.value == null) return;
    
    try {
      final message = await _chatService.sendMessage(
        chat.value!.id,
        text,
        type: 'text',
      );
      messages.insert(0, message);
      inputController.clear();
    } catch (e) {
      showError('发送失败');
    }
  }

  Future<void> sendVoiceMessage(String voicePath) async {
    // 实现语音消息发送
  }

  Future<void> sendImageMessage(String imagePath) async {
    // 实现图片消息发送
  }

  Future<void> sendFileMessage(String filePath) async {
    // 实现文件消息发送
  }

  void showUserProfile() {
    if (chat.value != null) {
      Get.toNamed('/user/${chat.value!.id}');
    }
  }

  void showChatOptions() {
    Get.bottomSheet(
      Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.search),
              title: const Text('搜索聊天记录'),
              onTap: () {
                Get.back();
                // 实现搜索功能
              },
            ),
            ListTile(
              leading: const Icon(Icons.delete_outline),
              title: const Text('清空聊天记录'),
              onTap: () {
                Get.back();
                _showClearConfirmDialog();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showClearConfirmDialog() {
    Get.dialog(
      AlertDialog(
        title: const Text('清空聊天记录'),
        content: const Text('确定要清空所有聊天记录吗？此操作不可恢复。'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Get.back();
              // 实现清空功能
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('清空'),
          ),
        ],
      ),
    );
  }

  void showMessageOptions(Message message) {
    Get.bottomSheet(
      Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.copy),
              title: const Text('复制'),
              onTap: () {
                Get.back();
                // 实现复制功能
              },
            ),
            ListTile(
              leading: const Icon(Icons.reply),
              title: const Text('回复'),
              onTap: () {
                Get.back();
                // 实现回复功能
              },
            ),
            ListTile(
              leading: const Icon(Icons.delete_outline),
              title: const Text('删除'),
              onTap: () {
                Get.back();
                // 实现删除功能
              },
            ),
          ],
        ),
      ),
    );
  }

  void startVoiceCall() {
    // 实现语音通话功能
  }

  void startVideoCall() {
    // 实现视频通话功能
  }
} 