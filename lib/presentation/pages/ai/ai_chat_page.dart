import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/ai/ai_chat_controller.dart';
import '../../widgets/ai_chat_message.dart';
import '../../widgets/ai_chat_input.dart';

class AIChatPage extends GetView<AIChatController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('AI助手'),
        actions: [
          IconButton(
            icon: Icon(Icons.settings),
            onPressed: () => Get.toNamed('/ai/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Obx(() => ListView.builder(
              reverse: true,
              itemCount: controller.messages.length,
              itemBuilder: (context, index) {
                final message = controller.messages[index];
                return AIChatMessage(message: message);
              },
            )),
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