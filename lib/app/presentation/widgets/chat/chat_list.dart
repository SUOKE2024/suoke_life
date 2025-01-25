import 'package:flutter/material.dart';
import '../../../data/models/chat_message.dart';
import 'chat_list_item.dart';

class ChatList extends StatelessWidget {
  final List<ChatMessage> messages;
  final Function(String) onTap;

  const ChatList({
    Key? key,
    required this.messages,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (messages.isEmpty) {
      return const Center(
        child: Text('暂无消息'),
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: messages.length,
      separatorBuilder: (context, index) => const Divider(),
      itemBuilder: (context, index) {
        final message = messages[index];
        return ChatListItem(
          message: message,
          onTap: () => onTap(message.roomId),
        );
      },
    );
  }
} 