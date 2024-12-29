import 'package:flutter/material.dart';
import '../../../data/models/chat_message.dart';

class ChatMessageList extends StatelessWidget {
  final List<ChatMessage> messages;
  final Function(String) onTapAvatar;
  final Function(ChatMessage) onLongPress;

  const ChatMessageList({
    Key? key,
    required this.messages,
    required this.onTapAvatar,
    required this.onLongPress,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        return ChatMessageItem(
          message: message,
          onTapAvatar: onTapAvatar,
          onLongPress: onLongPress,
        );
      },
    );
  }
}

class ChatMessageItem extends StatelessWidget {
  final ChatMessage message;
  final Function(String) onTapAvatar;
  final Function(ChatMessage) onLongPress;

  const ChatMessageItem({
    Key? key,
    required this.message,
    required this.onTapAvatar,
    required this.onLongPress,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onLongPress: () => onLongPress(message),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          mainAxisAlignment: message.isFromUser 
              ? MainAxisAlignment.end 
              : MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!message.isFromUser) ...[
              GestureDetector(
                onTap: () => onTapAvatar(message.senderId),
                child: CircleAvatar(
                  radius: 20,
                  // TODO: 使用实际的头像
                  child: Text(message.senderId[0].toUpperCase()),
                ),
              ),
              const SizedBox(width: 8),
            ],
            Flexible(
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: message.isFromUser 
                      ? Theme.of(context).primaryColor 
                      : Colors.grey[200],
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  message.content,
                  style: TextStyle(
                    color: message.isFromUser ? Colors.white : Colors.black,
                  ),
                ),
              ),
            ),
            if (message.isFromUser) ...[
              const SizedBox(width: 8),
              GestureDetector(
                onTap: () => onTapAvatar(message.senderId),
                child: CircleAvatar(
                  radius: 20,
                  // TODO: 使用实际的头像
                  child: Text(message.senderId[0].toUpperCase()),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
} 