import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../data/models/message.dart';
import 'message_bubble.dart';
import 'package:timeago/timeago.dart' as timeago;

class MessageItem extends StatelessWidget {
  final Message message;
  final VoidCallback onTap;
  final VoidCallback onLongPress;

  const MessageItem({
    Key? key,
    required this.message,
    required this.onTap,
    required this.onLongPress,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isMe = message.senderId == Get.find<AuthService>().currentUser.value?.id;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isMe) ...[
            CircleAvatar(
              radius: 16,
              backgroundImage: NetworkImage(message.metadata?['senderAvatar'] ?? ''),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                if (!isMe)
                  Padding(
                    padding: const EdgeInsets.only(left: 4, bottom: 4),
                    child: Text(
                      message.metadata?['senderName'] ?? '',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ),
                GestureDetector(
                  onTap: onTap,
                  onLongPress: onLongPress,
                  child: MessageBubble(
                    message: message,
                    isMe: isMe,
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        timeago.format(message.timestamp, locale: 'zh'),
                        style: TextStyle(
                          fontSize: 10,
                          color: Colors.grey[600],
                        ),
                      ),
                      if (isMe) ...[
                        const SizedBox(width: 4),
                        Icon(
                          message.isRead ? Icons.done_all : Icons.done,
                          size: 12,
                          color: message.isRead ? Colors.blue : Colors.grey[600],
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
          if (isMe) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundImage: NetworkImage(message.metadata?['senderAvatar'] ?? ''),
            ),
          ],
        ],
      ),
    );
  }
} 