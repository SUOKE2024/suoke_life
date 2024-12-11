import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/services/ai_service.dart';
import '../../../core/utils/logger.dart';

class LaokeController extends GetxController {
  final AIService _aiService = AIService();
  final textController = TextEditingController();
  final messages = <Map<String, dynamic>>[].obs;
  final isLoading = false.obs;
  
  static const String modelId = String.fromEnvironment(
    'DOUBAO_PRO_128K_EP',
    defaultValue: 'ep-20241207124106-4b5xn',
  );

  @override
  void onInit() {
    super.onInit();
    _addSystemMessage();
  }

  @override
  void onClose() {
    textController.dispose();
    super.onClose();
  }

  void _addSystemMessage() {
    messages.add({
      'isUser': false,
      'text': '您好，我是老克，您的知识助理。我可以帮您：\n'
          '• 解答专业问题\n'
          '• 推荐学习资源\n'
          '• 分享学习方法\n'
          '• 构建知识体系\n'
          '让我们开始探索知识的海洋吧！',
    });
  }

  Future<void> sendMessage() async {
    final text = textController.text.trim();
    if (text.isEmpty) return;

    // 添加用户消息
    messages.add({
      'isUser': true,
      'text': text,
    });

    // 清空输入框
    textController.clear();

    try {
      isLoading.value = true;

      // 调用AI服务
      final response = await _aiService.chat(
        modelId: modelId,
        messages: [
          {
            'role': 'system',
            'content': '你是老克，一个专注于知识分享和学习的AI助手。'
                '你的主要职责是：\n'
                '1. 解答用户的专业问题\n'
                '2. 推荐合适的学习资源\n'
                '3. 分享高效的学习方法\n'
                '4. 帮助用户构建知识体系\n'
                '请用专业、友好的语气与用户交流，注重知识的准确性和实用性。',
          },
          ...messages.map((msg) => {
            'role': msg['isUser'] ? 'user' : 'assistant',
            'content': msg['text'],
          }),
        ],
      );

      // 添加AI回复
      if (response != null) {
        messages.add({
          'isUser': false,
          'text': response,
        });
      } else {
        messages.add({
          'isUser': false,
          'text': '抱歉，我现在无法回答您的问题。请稍后再试。',
        });
      }

    } catch (e, stackTrace) {
      Logger.error('AI回复错误', e, stackTrace);
      messages.add({
        'isUser': false,
        'text': '抱歉，处理您的问题时出现错误。请稍后再试。',
      });
    } finally {
      isLoading.value = false;
    }
  }
} 