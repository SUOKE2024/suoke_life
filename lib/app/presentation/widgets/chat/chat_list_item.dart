import 'package:flutter/material.dart';
import '../../../data/models/chat_conversation.dart';
import 'package:timeago/timeago.dart' as timeago;

class ChatListItem extends StatelessWidget {
  final ChatConversation chat;
  final VoidCallback onTap;

  const ChatListItem({
    Key? key,
    required this.chat,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: onTap,
      leading: Stack(
        children: [
          CircleAvatar(
            backgroundImage: NetworkImage(chat.avatar),
            radius: 25,
            child: chat.type == 'ai' ? const Icon(Icons.smart_toy) : null,
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
      title: Row(
        children: [
          Text(
            chat.title,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
          if (chat.type == 'ai')
            Container(
              margin: const EdgeInsets.only(left: 8),
              padding: const EdgeInsets.symmetric(
                horizontal: 6,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: Colors.blue[100],
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                _getAiType(chat.title),
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.blue[800],
                ),
              ),
            ),
        ],
      ),
      subtitle: Text(
        _getLastMessageTime(chat.lastMessageAt),
        style: TextStyle(
          color: Colors.grey[600],
          fontSize: 12,
        ),
      ),
    );
  }

  String _getAiType(String title) {
    switch (title) {
      case '小艾':
        return '生活管家';
      case '老克':
        return '知识顾问';
      case '小克':
        return '商务助手';
      default:
        return 'AI助手';
    }
  }

  String _getLastMessageTime(DateTime? time) {
    if (time == null) return '';
    return timeago.format(time, locale: 'zh');
  }
} 