import 'package:get/get.dart';
import 'package:flutter/material.dart';
import 'package:suoke_app/app/presentation/controllers/chat/chat_detail_controller.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';
import 'package:suoke_app/app/data/models/chat_message.dart';

class MockChatDetailController extends ChatDetailController {
  MockChatDetailController({
    required String roomId,
    required SuokeService suokeService,
  }) : super(
    roomId: roomId,
    suokeService: suokeService,
  ) {
    // 初始化测试数据
    messages.value = [
      ChatMessage(
        id: '1',
        roomId: roomId,
        content: 'Test message',
        type: 'text',
        senderId: 'user',
        timestamp: DateTime.now(),
      ),
    ];
  }

  @override
  Future<void> loadMessages() async {
    // 不执行实际的加载操作
  }

  @override
  Future<void> sendMessage(String content, String type) async {
    // 不执行实际的发送操作
  }
} 