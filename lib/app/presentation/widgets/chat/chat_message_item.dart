import 'package:flutter/material.dart';
import '../../../data/models/chat_message.dart';
import 'package:timeago/timeago.dart' as timeago;

class ChatMessageItem extends StatelessWidget {
  final ChatMessage message;

  const ChatMessageItem({
    Key? key,
    required this.message,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isMe = !message.isAI;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        mainAxisAlignment: isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isMe) ...[
            CircleAvatar(
              child: message.isAI
                  ? const Icon(Icons.smart_toy)
                  : Text(message.senderName[0].toUpperCase()),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment:
                  isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isMe
                        ? Theme.of(context).primaryColor
                        : Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    message.content,
                    style: TextStyle(
                      color: isMe ? Colors.white : null,
                    ),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  timeago.format(message.timestamp, locale: 'zh'),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          if (isMe) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              child: Text(message.senderName[0].toUpperCase()),
            ),
          ],
        ],
      ),
    );
  }
} 