import 'package:flutter/material.dart';
import '../../../data/models/chat.dart';
import 'package:timeago/timeago.dart' as timeago;

class ChatListItem extends StatelessWidget {
  final Chat chat;
  final VoidCallback onTap;
  final VoidCallback onLongPress;

  const ChatListItem({
    Key? key,
    required this.chat,
    required this.onTap,
    required this.onLongPress,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: onTap,
      onLongPress: onLongPress,
      leading: Stack(
        children: [
          CircleAvatar(
            backgroundImage: NetworkImage(chat.avatar),
            radius: 24,
          ),
          if (chat.isOnline)
            Positioned(
              right: 0,
              bottom: 0,
              child: Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: Colors.green,
                  border: Border.all(
                    color: Theme.of(context).scaffoldBackgroundColor,
                    width: 2,
                  ),
                  borderRadius: BorderRadius.circular(6),
                ),
              ),
            ),
        ],
      ),
      title: Row(
        children: [
          Expanded(
            child: Text(
              chat.name,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          Text(
            timeago.format(chat.lastMessageTime, locale: 'zh'),
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
      subtitle: Row(
        children: [
          if (chat.isPinned)
            Padding(
              padding: const EdgeInsets.only(right: 4),
              child: Icon(
                Icons.push_pin,
                size: 14,
                color: Colors.grey[600],
              ),
            ),
          if (chat.isMuted)
            Padding(
              padding: const EdgeInsets.only(right: 4),
              child: Icon(
                Icons.notifications_off,
                size: 14,
                color: Colors.grey[600],
              ),
            ),
          Expanded(
            child: Text(
              chat.lastMessage,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: chat.unreadCount > 0 
                    ? Colors.black 
                    : Colors.grey[600],
              ),
            ),
          ),
          if (chat.unreadCount > 0)
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 6,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: Colors.red,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                chat.unreadCount.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                ),
              ),
            ),
        ],
      ),
    );
  }
} 