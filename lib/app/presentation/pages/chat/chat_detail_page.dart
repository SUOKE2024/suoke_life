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
      appBar: AppBar(title: Text(controller.conversation.title)),
      body: Column(
        children: [
          Expanded(
            child: ChatMessageList(
              messages: controller.messages,
              onTapAvatar: controller.onTapAvatar,
              onLongPressMessage: controller.onLongPressMessage,
            ),
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