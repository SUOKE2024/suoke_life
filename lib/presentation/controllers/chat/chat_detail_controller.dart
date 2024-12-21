import 'package:get/get.dart';
import '../../../models/message.dart';
import '../../../services/ai/ai_service.dart';
import '../../../services/storage/chat_storage_service.dart';

class ChatDetailController extends GetxController {
  final AIService _aiService;
  final ChatStorageService _storageService;
  final messages = <Message>[].obs;
  final isLoading = false.obs;
  final String chatAvatar;

  ChatDetailController(
    this._aiService,
    this._storageService,
    this.chatAvatar,
  );

  @override
  void onInit() {
    super.onInit();
    loadMessages();
  }

  Future<void> loadMessages() async {
    try {
      isLoading.value = true;
      final loadedMessages = await _storageService.getMessages();
      messages.assignAll(loadedMessages);
    } catch (e) {
      print('Error loading messages: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> sendTextMessage(String text) async {
    if (text.isEmpty) return;

    try {
      // 添加用户消息
      final userMessage = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: MessageType.text,
        content: text,
        isFromUser: true,
        timestamp: DateTime.now(),
      );
      messages.insert(0, userMessage);
      await _storageService.saveMessage(userMessage);

      // 获取AI响应
      final response = await _aiService.chat(text);
      
      // 添加AI响应消息
      final aiMessage = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: MessageType.text,
        content: response,
        isFromUser: false,
        timestamp: DateTime.now(),
      );
      messages.insert(0, aiMessage);
      await _storageService.saveMessage(aiMessage);
      
    } catch (e) {
      print('Error sending message: $e');
      Get.snackbar('错误', '发送消息失败');
    }
  }

  Future<void> sendVoiceMessage(String path) async {
    // 实现语音消息发送
  }

  Future<void> sendImageMessage(String path) async {
    // 实现图片消息发送
  }

  Future<void> sendVideoMessage(String path) async {
    // 实现视频消息发送
  }
} 