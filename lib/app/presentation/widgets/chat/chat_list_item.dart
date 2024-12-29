import 'package:flutter/material.dart';
import 'package:timeago/timeago.dart' as timeago;
import '../../../data/models/chat.dart';

class ChatListItem extends StatelessWidget {
  final Chat chat;
  final VoidCallback onTap;

  const ChatListItem({
    Key? key,
    required this.chat,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Stack(
        children: [
          CircleAvatar(
            backgroundImage: NetworkImage(chat.avatar ?? ''),
            child: chat.isAI ? const Icon(Icons.smart_toy) : null,
          ),
          if (chat.unreadCount > 0)
            Positioned(
              right: 0,
              top: 0,
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: Colors.red,
                  borderRadius: BorderRadius.circular(10),
                ),
                constraints: const BoxConstraints(
                  minWidth: 20,
                  minHeight: 20,
                ),
                child: Text(
                  chat.unreadCount.toString(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
        ],
      ),
      title: Text(chat.title),
      subtitle: Text(chat.lastMessage ?? ''),
      trailing: Text(
        timeago.format(chat.lastMessageTime ?? DateTime.now(), locale: 'zh'),
        style: Theme.of(context).textTheme.bodySmall,
      ),
      onTap: onTap,
    );
  }
} 