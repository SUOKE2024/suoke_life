import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/ai/ai_chat_detail_controller.dart';
import '../../widgets/ai_chat_message.dart';
import '../../widgets/ai_chat_input.dart';

class AIChatDetailPage extends GetView<AIChatDetailController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Obx(() => Text(controller.chatTitle.value)),
        actions: [
          IconButton(
            icon: Icon(Icons.info_outline),
            onPressed: () => controller.showChatInfo(),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Obx(() {
              if (controller.isLoading.value) {
                return Center(child: CircularProgressIndicator());
              }
              
              return ListView.builder(
                reverse: true,
                padding: EdgeInsets.all(16),
                itemCount: controller.messages.length,
                itemBuilder: (context, index) {
                  final message = controller.messages[index];
                  return AIChatMessage(message: message);
                },
              );
            }),
          ),
          AIChatInput(
            onSendText: controller.sendMessage,
            onSendVoice: controller.sendVoiceMessage,
          ),
        ],
      ),
    );
  }
} 