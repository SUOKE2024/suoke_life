import 'package:flutter/material.dart';

class ChatListItem extends StatelessWidget {
  final String title;
  final String lastMessage;
  final String time;
  final VoidCallback? onTap;

  const ChatListItem({
    Key? key,
    required this.title,
    required this.lastMessage,
    required this.time,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(title),
      subtitle: Text(lastMessage),
      trailing: Text(time),
      onTap: onTap,
    );
  }
} 