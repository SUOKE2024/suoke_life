import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../widgets/chat_input.dart';

abstract class BaseAIChatPage extends StatelessWidget {
  final String title;
  final String avatar;
  
  const BaseAIChatPage({
    Key? key,
    required this.title,
    required this.avatar,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        actions: buildActions(),
      ),
      body: Column(
        children: [
          Expanded(
            child: buildMessageList(),
          ),
          buildInputArea(),
        ],
      ),
    );
  }

  List<Widget> buildActions() => [];
  
  Widget buildMessageList();
  
  Widget buildInputArea() {
    return ChatInput(
      onSendText: onSendText,
      onSendVoice: onSendVoice,
      onSendImage: onSendImage,
      onSendVideo: onSendVideo,
    );
  }

  void onSendText(String text);
  void onSendVoice(String path);
  void onSendImage(String path);
  void onSendVideo(String path);
} 