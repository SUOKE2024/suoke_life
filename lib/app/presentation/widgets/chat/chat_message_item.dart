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
    final isMe = message.senderId == 'current_user';

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isMe) ...[
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
            child: GestureDetector(
              onLongPress: onLongPress,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isMe ? Colors.blue[100] : Colors.grey[200],
                  borderRadius: BorderRadius.circular(16),
                ),
                child: _buildMessageContent(),
              ),
            ),
          ),
          if (isMe) ...[
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
    );
  }

  Widget _buildMessageContent() {
    switch (message.type) {
      case 'text':
        return Text(message.content);
      case 'image':
        return Image.network(message.content);
      case 'voice':
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.play_arrow,
              color: Colors.grey[600],
            ),
            const SizedBox(width: 4),
            Text('${message.duration}″'),
          ],
        );
      default:
        return const Text('不支持的消息类型');
    }
  }
} 