import 'package:get/get.dart';
import '../../models/message.dart';
import '../../services/ai/ai_service.dart';
import '../../services/storage/chat_storage_service.dart';

abstract class BaseChatController extends GetxController {
  final messages = <Message>[].obs;
  final isLoading = false.obs;
  
  final AIService aiService;
  final ChatStorageService storageService;

  BaseChatController({
    required this.aiService,
    required this.storageService,
  });

  @override
  void onInit() {
    super.onInit();
    loadMessages();
  }

  Future<void> loadMessages() async {
    try {
      isLoading.value = true;
      final storedMessages = await storageService.getMessages();
      messages.assignAll(storedMessages);
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> sendTextMessage(String text) async {
    final message = Message(
      id: DateTime.now().toString(),
      type: MessageType.text,
      content: text,
      isFromUser: true,
      timestamp: DateTime.now(),
    );
    
    messages.add(message);
    await storageService.saveMessage(message);
    
    // 获取AI回复
    final response = await aiService.getResponse(text);
    final aiMessage = Message(
      id: DateTime.now().toString(),
      type: MessageType.text,
      content: response,
      isFromUser: false,
      timestamp: DateTime.now(),
    );
    
    messages.add(aiMessage);
    await storageService.saveMessage(aiMessage);
  }

  Future<void> sendVoiceMessage(String path) async {
    // 1. 上传语音文件
    final url = await storageService.uploadVoice(path);
    
    // 2. 语音转文字
    final text = await aiService.speechToText(path);
    
    final message = Message(
      id: DateTime.now().toString(),
      type: MessageType.voice,
      content: url,
      isFromUser: true,
      timestamp: DateTime.now(),
      metadata: {'text': text},
    );
    
    messages.add(message);
    await storageService.saveMessage(message);
    
    // 3. 获取AI回复
    final response = await aiService.getResponse(text);
    final aiMessage = Message(
      id: DateTime.now().toString(),
      type: MessageType.text,
      content: response,
      isFromUser: false,
      timestamp: DateTime.now(),
    );
    
    messages.add(aiMessage);
    await storageService.saveMessage(aiMessage);
  }

  Future<void> sendImageMessage(String path) async {
    // 1. 上传图片
    final url = await storageService.uploadImage(path);
    
    // 2. 图像识别
    final analysis = await aiService.analyzeImage(path);
    
    final message = Message(
      id: DateTime.now().toString(),
      type: MessageType.image,
      content: url,
      isFromUser: true,
      timestamp: DateTime.now(),
      metadata: {'analysis': analysis},
    );
    
    messages.add(message);
    await storageService.saveMessage(message);
    
    // 3. 获取AI回复
    final response = await aiService.getImageResponse(analysis);
    final aiMessage = Message(
      id: DateTime.now().toString(),
      type: MessageType.text, 
      content: response,
      isFromUser: false,
      timestamp: DateTime.now(),
    );
    
    messages.add(aiMessage);
    await storageService.saveMessage(aiMessage);
  }

  Future<void> sendVideoMessage(String path) async {
    // 1. 生成缩略图
    final thumbnail = await storageService.generateThumbnail(path);
    
    // 2. 上传视频
    final url = await storageService.uploadVideo(path);
    
    final message = Message(
      id: DateTime.now().toString(),
      type: MessageType.video,
      content: url,
      isFromUser: true,
      timestamp: DateTime.now(),
      thumbnail: thumbnail,
    );
    
    messages.add(message);
    await storageService.saveMessage(message);
  }
} 