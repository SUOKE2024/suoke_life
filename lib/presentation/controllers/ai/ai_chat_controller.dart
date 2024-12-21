import 'package:get/get.dart';
import '../../../models/message.dart';
import '../../../services/ai/ai_service.dart';
import '../../../services/storage/chat_storage_service.dart';
import '../../../services/voice/voice_service.dart';

class AIChatController extends GetxController {
  final AIService _aiService;
  final ChatStorageService _storageService;
  final VoiceService _voiceService;
  
  final messages = <Message>[].obs;
  final isLoading = false.obs;
  final isRecording = false.obs;

  AIChatController(
    this._aiService,
    this._storageService,
    this._voiceService,
  );

  @override
  void onInit() {
    super.onInit();
    loadMessages();
  }

  Future<void> loadMessages() async {
    try {
      isLoading.value = true;
      final history = await _storageService.getRecentMessages();
      messages.value = history;
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
    try {
      isLoading.value = true;
      
      // 1. 语音转文字
      final text = await _voiceService.speechToText(path);
      
      // 2. 发送文字消息
      await sendMessage(text);
      
      // 3. 如果启用了语音回复，将AI回复转换为语音
      final settings = await _aiService.getSettings();
      if (settings['voiceEnabled'] == true) {
        final lastAiMessage = messages.firstWhere((m) => !m.isFromUser);
        await _voiceService.textToSpeech(lastAiMessage.content);
      }
      
    } catch (e) {
      Get.snackbar('错误', '发送语音消息失败: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> startRecording() async {
    try {
      await _voiceService.startRecording();
      isRecording.value = true;
    } catch (e) {
      Get.snackbar('错误', '开始录音失败: $e');
    }
  }

  Future<void> stopRecording() async {
    try {
      final path = await _voiceService.stopRecording();
      isRecording.value = false;
      if (path != null) {
        await sendVoiceMessage(path);
      }
    } catch (e) {
      Get.snackbar('错误', '停止录音失败: $e');
      isRecording.value = false;
    }
  }

  @override
  void onClose() {
    _voiceService.dispose();
    super.onClose();
  }
} 