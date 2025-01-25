import 'package:flutter/material.dart';
import '../../../data/models/chat_message.dart';
import 'package:timeago/timeago.dart' as timeago;

class ChatListItem extends StatelessWidget {
  final ChatMessage message;
  final VoidCallback onTap;

  const ChatListItem({
    Key? key,
    required this.message,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        child: message.isAI
            ? const Icon(Icons.smart_toy)
            : Text(message.senderName[0].toUpperCase()),
      ),
      title: Text(message.senderName),
      subtitle: Text(message.content),
      trailing: Text(
        timeago.format(message.timestamp, locale: 'zh'),
        style: Theme.of(context).textTheme.bodySmall,
      ),
      onTap: onTap,
    );
  }
} 