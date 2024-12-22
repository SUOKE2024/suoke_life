import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import '../presentation/controllers/ai_chat_controller.dart';
import '../services/chat_service.dart';
import '../services/doubao_service.dart';

void main() {
  group('AI聊天测试', () {
    late AiChatController controller;
    late ChatService chatService;
    late DouBaoService doubaoService;

    setUp(() {
      Get.put(ChatService());
      Get.put(DouBaoService());
      Get.put(AiChatController());
      
      controller = Get.find<AiChatController>();
      chatService = Get.find<ChatService>();
      doubaoService = Get.find<DouBaoService>();
    });

    test('模型切换测试', () {
      expect(controller.selectedModel.value, equals('xiaoai'));
      
      controller.changeModel('laoke');
      expect(controller.selectedModel.value, equals('laoke'));
      
      controller.changeModel('xiaoke');
      expect(controller.selectedModel.value, equals('xiaoke'));
    });

    test('消息发送测试', () async {
      await controller.sendTextMessage('测试消息');
      expect(controller.messages.length, equals(2)); // 用户���息和AI回复
      
      final lastMessage = controller.messages.first;
      expect(lastMessage.senderId, equals(ChatMessage.senderAi));
    });

    test('环境配置测试', () {
      expect(EnvConfig.to.doubaoApiKey, isNotEmpty);
      expect(EnvConfig.to.doubaoPro32kEp, isNotEmpty);
      expect(EnvConfig.to.doubaoPro128kEp, isNotEmpty);
    });
  });
} 