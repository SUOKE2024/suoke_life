import 'package:flutter/material.dart';
import '../../../data/models/chat_message.dart';

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

    return ListView.builder(
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        return ListTile(
          leading: CircleAvatar(
            child: Text(message.senderId[0].toUpperCase()),
          ),
          title: Text(message.senderId),
          subtitle: Text(message.content),
          trailing: Text(
            _formatTime(message.timestamp),
            style: Theme.of(context).textTheme.bodySmall,
          ),
          onTap: () => onTap(message.roomId),
        );
      },
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);

    if (difference.inDays > 0) {
      return '${difference.inDays}天前';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}小时前';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}分钟前';
    } else {
      return '刚刚';
    }
  }
} 