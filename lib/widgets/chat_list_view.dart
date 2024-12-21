import 'package:flutter/material.dart';

class ChatListView extends StatelessWidget {
  final List<ChatItem> items;

  const ChatListView({
    Key? key,
    required this.items,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: items.length,
      itemBuilder: (context, index) => items[index],
    );
  }
}

class ChatItem extends StatelessWidget {
  final String avatar;
  final String title;
  final String? subtitle;
  final String? lastMessage;
  final DateTime? lastMessageTime;
  final VoidCallback onTap;

  const ChatItem({
    Key? key,
    required this.avatar,
    required this.title,
    this.subtitle,
    this.lastMessage,
    this.lastMessageTime,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundImage: AssetImage('assets/images/ai/$avatar'),
        ),
        title: Text(title),
        subtitle: subtitle != null || lastMessage != null
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (subtitle != null) Text(subtitle!),
                  if (lastMessage != null)
                    Text(
                      lastMessage!,
                      style: TextStyle(color: Colors.grey[600]),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              )
            : null,
        trailing: lastMessageTime != null
            ? Text(
                _formatTime(lastMessageTime!),
                style: TextStyle(color: Colors.grey[600]),
              )
            : null,
        onTap: onTap,
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);

    if (difference.inMinutes < 60) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}天前';
    } else {
      return '${time.month}-${time.day}';
    }
  }
} 