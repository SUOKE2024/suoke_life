import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/chat/chat_detail_controller.dart';
import '../../../routes/app_routes.dart';
import '../../../widgets/chat_message.dart';
import '../../../widgets/chat_input.dart';

class ChatDetailPage extends GetView<ChatDetailController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('聊天'),
        actions: [
          IconButton(
            icon: Icon(Icons.settings),
            onPressed: () => Get.toNamed(AppRoutes.CHAT_SETTINGS),
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
                return ChatMessage(
                  message: message,
                  avatar: controller.chatAvatar,
                );
              },
            )),
          ),
          ChatInput(
            onSendText: controller.sendTextMessage,
            onSendVoice: controller.sendVoiceMessage,
            onSendImage: controller.sendImageMessage,
            onSendVideo: controller.sendVideoMessage,
          ),
        ],
      ),
    );
  }
} 