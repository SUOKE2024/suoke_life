import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/ai_chat_controller.dart';
import '../../widgets/chat/chat_input.dart';
import '../../widgets/chat/chat_message.dart';

class AiChatPage extends GetView<AiChatController> {
  const AiChatPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(controller.assistantName),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Get.toNamed('/ai/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          // 聊天消息列表
          Expanded(
            child: Obx(() => ListView.builder(
              reverse: true,
              itemCount: controller.messages.length,
              itemBuilder: (context, index) {
                final message = controller.messages[index];
                return ChatMessage(message: message);
              },
            )),
          ),

          // 输入框
          ChatInput(
            onSend: controller.sendMessage,
            onVoice: controller.startVoiceInput,
          ),
        ],
      ),
    );
  }
} 