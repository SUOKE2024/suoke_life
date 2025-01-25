import 'package:flutter/material.dart';
import '../../../domain/models/chat_message.dart';

class MessageList extends StatelessWidget {
  final List<ChatMessage> messages;

  const MessageList({
    super.key,
    required this.messages,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      reverse: true,
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        return ListTile(
          title: Text(message.content),
          subtitle: Text(message.timestamp.toString()),
          leading: message.isFromUser 
              ? null 
              : const CircleAvatar(child: Icon(Icons.person)),
          trailing: message.isFromUser
              ? const CircleAvatar(child: Icon(Icons.person))
              : null,
        );
      },
    );
  }
} 