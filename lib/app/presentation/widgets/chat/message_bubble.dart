import 'package:flutter/material.dart';
import '../../../data/models/message.dart';

class MessageBubble extends StatelessWidget {
  final Message message;
  final bool isMe;

  const MessageBubble({
    Key? key,
    required this.message,
    required this.isMe,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxWidth: MediaQuery.of(context).size.width * 0.7,
      ),
      decoration: BoxDecoration(
        color: isMe ? Colors.blue : Theme.of(context).cardColor,
        borderRadius: BorderRadius.only(
          topLeft: const Radius.circular(16),
          topRight: const Radius.circular(16),
          bottomLeft: Radius.circular(isMe ? 16 : 4),
          bottomRight: Radius.circular(isMe ? 4 : 16),
        ),
      ),
      child: _buildMessageContent(context),
    );
  }

  Widget _buildMessageContent(BuildContext context) {
    switch (message.type) {
      case 'text':
        return Padding(
          padding: const EdgeInsets.all(12),
          child: Text(
            message.content,
            style: TextStyle(
              color: isMe ? Colors.white : Theme.of(context).textTheme.bodyLarge?.color,
            ),
          ),
        );
      case 'image':
        return ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Image.network(
            message.content,
            fit: BoxFit.cover,
          ),
        );
      case 'voice':
        return _buildVoiceMessage(context);
      case 'video':
        return _buildVideoMessage(context);
      case 'file':
        return _buildFileMessage(context);
      default:
        return const SizedBox();
    }
  }

  Widget _buildVoiceMessage(BuildContext context) {
    final duration = message.metadata?['duration'] as int? ?? 0;
    return Container(
      padding: const EdgeInsets.all(12),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.play_arrow,
            color: isMe ? Colors.white : Theme.of(context).iconTheme.color,
          ),
          const SizedBox(width: 8),
          Text(
            '${duration}s',
            style: TextStyle(
              color: isMe ? Colors.white : Theme.of(context).textTheme.bodyLarge?.color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVideoMessage(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: [
        Image.network(
          message.metadata?['thumbnail'] ?? '',
          fit: BoxFit.cover,
        ),
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.5),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.play_arrow,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildFileMessage(BuildContext context) {
    final fileName = message.metadata?['fileName'] ?? '';
    final fileSize = message.metadata?['fileSize'] ?? '';
    return Container(
      padding: const EdgeInsets.all(12),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.insert_drive_file,
            color: isMe ? Colors.white : Theme.of(context).iconTheme.color,
          ),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                fileName,
                style: TextStyle(
                  color: isMe ? Colors.white : Theme.of(context).textTheme.bodyLarge?.color,
                ),
              ),
              Text(
                fileSize,
                style: TextStyle(
                  fontSize: 12,
                  color: isMe ? Colors.white70 : Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
} 