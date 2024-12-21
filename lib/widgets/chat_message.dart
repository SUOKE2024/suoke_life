import 'package:flutter/material.dart';
import '../models/message.dart';

class ChatMessage extends StatelessWidget {
  final Message message;
  final String avatar;

  const ChatMessage({
    Key? key,
    required this.message,
    required this.avatar,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isUser = message.isFromUser;
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              backgroundImage: AssetImage('assets/images/ai/$avatar'),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isUser ? Colors.blue : Colors.grey[200],
                borderRadius: BorderRadius.circular(16),
              ),
              child: buildMessageContent(),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            const CircleAvatar(
              child: Icon(Icons.person),
            ),
          ],
        ],
      ),
    );
  }

  Widget buildMessageContent() {
    switch (message.type) {
      case MessageType.text:
        return Text(
          message.content,
          style: TextStyle(
            color: message.isFromUser ? Colors.white : Colors.black,
          ),
        );
      case MessageType.image:
        return Image.network(message.content);
      case MessageType.voice:
        return buildVoiceMessage();
      case MessageType.video:
        return buildVideoMessage();
      default:
        return const SizedBox();
    }
  }

  Widget buildVoiceMessage() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          Icons.play_arrow,
          color: message.isFromUser ? Colors.white : Colors.black,
        ),
        const SizedBox(width: 4),
        Text(
          '${message.duration}″',
          style: TextStyle(
            color: message.isFromUser ? Colors.white : Colors.black,
          ),
        ),
      ],
    );
  }

  Widget buildVideoMessage() {
    return Stack(
      alignment: Alignment.center,
      children: [
        Image.network(message.thumbnail ?? ''),
        Icon(
          Icons.play_circle_fill,
          size: 48,
          color: Colors.white.withOpacity(0.8),
        ),
      ],
    );
  }
} 