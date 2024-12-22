import 'package:flutter/material.dart';
import '../../../data/models/chat_message.dart';
import 'chat_message_item.dart';

class ChatMessageList extends StatelessWidget {
  final List<ChatMessage> messages;
  final Function(String) onTapAvatar;
  final Function(ChatMessage) onLongPressMessage;

  const ChatMessageList({
    Key? key,
    required this.messages,
    required this.onTapAvatar,
    required this.onLongPressMessage,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      reverse: true,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        return ChatMessageItem(
          message: message,
          onTapAvatar: () => onTapAvatar(message.senderId),
          onLongPress: () => onLongPressMessage(message),
        );
      },
    );
  }
} 