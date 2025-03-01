import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../domain/entities/message.dart';
import '../../ai_agents/models/ai_agent.dart';

class MessageBubble extends StatelessWidget {
  final Message message;
  final bool isFromCurrentUser;
  final AIAgent? agent;
  final VoidCallback? onLongPress;
  
  const MessageBubble({
    Key? key,
    required this.message,
    required this.isFromCurrentUser,
    this.agent,
    this.onLongPress,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Row(
        mainAxisAlignment: isFromCurrentUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isFromCurrentUser) _buildAvatar(),
          const SizedBox(width: 8),
          Flexible(
            child: GestureDetector(
              onLongPress: onLongPress,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
                decoration: BoxDecoration(
                  color: _getBubbleColor(context),
                  borderRadius: _getBubbleBorderRadius(),
                ),
                child: Column(
                  crossAxisAlignment: isFromCurrentUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                  children: [
                    if (!isFromCurrentUser && agent != null)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 4.0),
                        child: Text(
                          agent!.name,
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                            color: agent!.color,
                          ),
                        ),
                      ),
                    _buildMessageContent(),
                    const SizedBox(height: 4),
                    Text(
                      _formatTime(message.timestamp),
                      style: TextStyle(
                        fontSize: 10,
                        color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          if (isFromCurrentUser) _buildStatus(),
        ],
      ),
    );
  }
  
  Widget _buildAvatar() {
    if (agent != null) {
      return CircleAvatar(
        radius: 18,
        backgroundColor: agent!.color.withOpacity(0.2),
        child: Text(
          agent!.name.substring(0, 1),
          style: TextStyle(
            color: agent!.color,
            fontWeight: FontWeight.bold,
          ),
        ),
      );
    } else {
      return const CircleAvatar(
        radius: 18,
        backgroundColor: Colors.grey,
        child: Icon(
          Icons.person,
          color: Colors.white,
          size: 20,
        ),
      );
    }
  }
  
  Widget _buildMessageContent() {
    switch (message.type) {
      case MessageType.text:
        return Text(
          message.content,
          style: const TextStyle(fontSize: 16),
        );
      case MessageType.image:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                message.content,
                width: 200,
                fit: BoxFit.cover,
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  return SizedBox(
                    width: 200,
                    height: 150,
                    child: Center(
                      child: CircularProgressIndicator(
                        value: loadingProgress.expectedTotalBytes != null
                            ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes!
                            : null,
                      ),
                    ),
                  );
                },
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    width: 200,
                    height: 150,
                    color: Colors.grey[200],
                    child: const Center(
                      child: Icon(Icons.error),
                    ),
                  );
                },
              ),
            ),
            if (message.metadata != null && message.metadata!['caption'] != null)
              Padding(
                padding: const EdgeInsets.only(top: 8.0),
                child: Text(
                  message.metadata!['caption'],
                  style: const TextStyle(fontSize: 14),
                ),
              ),
          ],
        );
      case MessageType.system:
        return Container(
          padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 12.0),
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            message.content,
            style: const TextStyle(
              fontSize: 14,
              fontStyle: FontStyle.italic,
              color: Colors.black54,
            ),
          ),
        );
      default:
        return Text(
          message.content,
          style: const TextStyle(fontSize: 16),
        );
    }
  }
  
  Widget _buildStatus() {
    IconData? icon;
    Color color = Colors.grey;
    
    switch (message.status) {
      case MessageStatus.sending:
        return const SizedBox(
          width: 12,
          height: 12,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.grey),
          ),
        );
      case MessageStatus.sent:
        icon = Icons.check;
        break;
      case MessageStatus.delivered:
        icon = Icons.done_all;
        break;
      case MessageStatus.read:
        icon = Icons.done_all;
        color = Colors.blue;
        break;
      case MessageStatus.failed:
        icon = Icons.error_outline;
        color = Colors.red;
        break;
    }
    
    return Icon(
      icon,
      size: 16,
      color: color,
    );
  }
  
  Color _getBubbleColor(BuildContext context) {
    if (isFromCurrentUser) {
      return Theme.of(context).primaryColor.withOpacity(0.2);
    } else if (agent != null) {
      return agent!.color.withOpacity(0.1);
    } else {
      return Theme.of(context).cardColor;
    }
  }
  
  BorderRadius _getBubbleBorderRadius() {
    const double radius = 16.0;
    
    if (isFromCurrentUser) {
      return const BorderRadius.only(
        topLeft: Radius.circular(radius),
        topRight: Radius.circular(radius),
        bottomLeft: Radius.circular(radius),
        bottomRight: Radius.circular(4.0),
      );
    } else {
      return const BorderRadius.only(
        topLeft: Radius.circular(4.0),
        topRight: Radius.circular(radius),
        bottomLeft: Radius.circular(radius),
        bottomRight: Radius.circular(radius),
      );
    }
  }
  
  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final messageDate = DateTime(time.year, time.month, time.day);
    
    String timeStr = '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
    
    if (messageDate == today) {
      return timeStr;
    } else if (messageDate == yesterday) {
      return '昨天 $timeStr';
    } else {
      return '${time.month}月${time.day}日 $timeStr';
    }
  }
}