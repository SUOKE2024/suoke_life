import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/chat/chat_detail_controller.dart';
import '../../widgets/chat/message_bubble.dart';
import '../../widgets/chat/chat_input_bar.dart';

class ChatDetailPage extends GetView<ChatDetailController> {
  final String? assistant;
  
  const ChatDetailPage({Key? key, this.assistant}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(assistant ?? 'Chat'),
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () => Get.toNamed('/chat/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Obx(() => ListView.builder(
              reverse: true,
              padding: const EdgeInsets.all(16),
              itemCount: controller.messages.length,
              itemBuilder: (context, index) {
                final message = controller.messages[index];
                return MessageBubble(
                  message: message,
                  isMe: message.senderId == 'user',
                );
              },
            )),
          ),
          ChatInputBar(
            onSend: controller.sendMessage,
            onVoice: controller.startVoiceInput,
            onAttachment: controller.showAttachmentOptions,
          ),
        ],
      ),
    );
  }
} 