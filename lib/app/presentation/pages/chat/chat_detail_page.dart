import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/chat_detail_controller.dart';
import '../../widgets/chat/chat_message_list.dart';
import '../../widgets/chat/chat_input_bar.dart';

class ChatDetailPage extends GetView<ChatDetailController> {
  const ChatDetailPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(controller.conversation.title),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: controller.showSettings,
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Obx(() => ChatMessageList(
              messages: controller.messages,
              onLongPress: controller.onLongPressMessage,
              onTapAvatar: controller.onTapAvatar,
            )),
          ),
          ChatInputBar(
            onSendText: controller.sendMessage,
            onVoiceStart: null,
            onVoiceEnd: null,
            onVoiceCancel: null,
            onTapExtra: null,
          ),
        ],
      ),
    );
  }
} 