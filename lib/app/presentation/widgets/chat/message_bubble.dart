import 'package:flutter/material.dart';
import '../../../data/models/chat_message.dart';
import 'package:timeago/timeago.dart' as timeago;

class MessageBubble extends StatelessWidget {
  final ChatMessage message;
  final bool isMe;

  const MessageBubble({
    Key? key,
    required this.message,
    required this.isMe,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
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
              crossAxisAlignment: isMe 
                  ? CrossAxisAlignment.end 
                  : CrossAxisAlignment.start,
              children: [
                if (!isMe)
                  Text(
                    message.senderName,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: isMe 
                        ? Theme.of(context).primaryColor
                        : Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    message.content,
                    style: TextStyle(
                      color: isMe ? Colors.white : null,
                    ),
                  ),
                ),
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