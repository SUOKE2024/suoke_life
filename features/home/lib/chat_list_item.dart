import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class ChatListItem extends StatelessWidget {
  final String title;
  final String lastMessage;
  final String time;

  const ChatListItem({
    Key? key,
    required this.title,
    required this.lastMessage,
    required this.time,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const CircleAvatar(
        backgroundImage: AssetImage('assets/images/user_avatar.png'),
      ),
      title: Text(title),
      subtitle: Text(lastMessage),
      trailing: Text(time),
      onTap: () {
        context.go('/chat_interaction');
      },
    );
  }
} 