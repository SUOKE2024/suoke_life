import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/ai_chat_controller.dart';
import '../../widgets/chat/chat_input.dart';
import '../../widgets/chat/chat_message.dart';

class AIChatPage extends GetView<AIChatController> {
  const AIChatPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(controller.aiName),
            Text(
              controller.aiDescription,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: controller.showOptions,
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Obx(() {
              if (controller.isLoading.value && controller.messages.isEmpty) {
                return const Center(child: CircularProgressIndicator());
              }
              return ListView.builder(
                padding: const EdgeInsets.all(16),
                reverse: true,
                itemCount: controller.messages.length,
                itemBuilder: (context, index) {
                  final message = controller.messages[index];
                  return ChatMessage(
                    message: message,
                    onLongPress: () => controller.showMessageOptions(message),
                  );
                },
              );
            }),
          ),
          ChatInput(
            onSend: controller.sendMessage,
            onVoice: controller.startVoiceInput,
          ),
        ],
      ),
    );
  }
} 