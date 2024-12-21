import 'package:flutter/material.dart';
import 'base_ai_chat_page.dart';
import '../../controllers/chat/xiaoi_chat_controller.dart';

class XiaoiChatPage extends BaseAIChatPage {
  XiaoiChatPage({Key? key}) : super(
    key: key,
    title: '小艾',
    avatar: 'xiaoi.png',
  );

  final controller = Get.put(XiaoiChatController());

  @override
  List<Widget> buildActions() => [
    IconButton(
      icon: const Icon(Icons.info_outline),
      onPressed: () => Get.to(() => XiaoiProfilePage()),
    ),
  ];

  @override
  Widget buildMessageList() {
    return Obx(() => ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: controller.messages.length,
      itemBuilder: (context, index) {
        final msg = controller.messages[index];
        return ChatMessage(
          message: msg,
          avatar: avatar,
        );
      },
    ));
  }

  @override
  void onSendText(String text) {
    controller.sendTextMessage(text);
  }

  @override
  void onSendVoice(String path) {
    controller.sendVoiceMessage(path);
  }

  @override
  void onSendImage(String path) {
    controller.sendImageMessage(path);
  }

  @override
  void onSendVideo(String path) {
    controller.sendVideoMessage(path);
  }
} 