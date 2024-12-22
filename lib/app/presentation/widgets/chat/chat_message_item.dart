import 'package:flutter/material.dart';
import '../../../data/models/chat_message.dart';

class ChatMessageItem extends StatelessWidget {
  final ChatMessage message;
  final VoidCallback onTapAvatar;
  final VoidCallback onLongPress;

  const ChatMessageItem({
    Key? key,
    required this.message,
    required this.onTapAvatar,
    required this.onLongPress,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isFromUser = message.isFromUser;

    return GestureDetector(
      onLongPress: onLongPress,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          mainAxisAlignment:
              isFromUser ? MainAxisAlignment.end : MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!isFromUser) ...[
              GestureDetector(
                onTap: onTapAvatar,
                child: CircleAvatar(
                  backgroundImage: NetworkImage(message.senderAvatar),
                  radius: 20,
                ),
              ),
              const SizedBox(width: 8),
            ],
            Flexible(
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isFromUser ? Colors.blue[100] : Colors.grey[200],
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(message.content),
              ),
            ),
            if (isFromUser) ...[
              const SizedBox(width: 8),
              GestureDetector(
                onTap: onTapAvatar,
                child: CircleAvatar(
                  backgroundImage: NetworkImage(message.senderAvatar),
                  radius: 20,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
} 