import 'package:flutter/material.dart';
import '../../models/chat_message.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({
    Key? key,
    required this.message,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isUser = message.sender == MessageSender.user;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) _buildAvatar(context),
          const SizedBox(width: 8),
          Flexible(
            child: Column(
              crossAxisAlignment:
                  isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isUser
                        ? Theme.of(context).primaryColor
                        : Colors.grey[200],
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: _buildMessageContent(context),
                ),
                if (message.healthData != null)
                  _buildHealthDataPreview(context),
              ],
            ),
          ),
          const SizedBox(width: 8),
          if (isUser) _buildAvatar(context),
        ],
      ),
    );
  }

  Widget _buildAvatar(BuildContext context) {
    return CircleAvatar(
      radius: 20,
      backgroundColor: message.sender == MessageSender.user
          ? Theme.of(context).primaryColor
          : Colors.grey[300],
      child: Icon(
        message.sender == MessageSender.user ? Icons.person : Icons.smart_toy,
        color: Colors.white,
      ),
    );
  }

  Widget _buildMessageContent(BuildContext context) {
    switch (message.type) {
      case MessageType.text:
        return Text(
          message.content,
          style: TextStyle(
            color: message.sender == MessageSender.user
                ? Colors.white
                : Colors.black,
          ),
        );
      case MessageType.voice:
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.mic,
              color: message.sender == MessageSender.user
                  ? Colors.white
                  : Colors.black54,
            ),
            const SizedBox(width: 8),
            Text(
              '语音消息',
              style: TextStyle(
                color: message.sender == MessageSender.user
                    ? Colors.white
                    : Colors.black,
              ),
            ),
          ],
        );
      case MessageType.image:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (message.imageUrl != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  message.imageUrl!,
                  width: 200,
                  fit: BoxFit.cover,
                ),
              ),
            if (message.content.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  message.content,
                  style: TextStyle(
                    color: message.sender == MessageSender.user
                        ? Colors.white
                        : Colors.black,
                  ),
                ),
              ),
          ],
        );
      case MessageType.video:
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.videocam,
              color: message.sender == MessageSender.user
                  ? Colors.white
                  : Colors.black54,
            ),
            const SizedBox(width: 8),
            Text(
              '视频消息',
              style: TextStyle(
                color: message.sender == MessageSender.user
                    ? Colors.white
                    : Colors.black,
              ),
            ),
          ],
        );
      case MessageType.healthReport:
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.health_and_safety,
              color: message.sender == MessageSender.user
                  ? Colors.white
                  : Colors.black54,
            ),
            const SizedBox(width: 8),
            Text(
              '健康报告',
              style: TextStyle(
                color: message.sender == MessageSender.user
                    ? Colors.white
                    : Colors.black,
              ),
            ),
          ],
        );
    }
  }

  Widget _buildHealthDataPreview(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(top: 8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '健康数据',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const Divider(),
            ...message.healthData!.entries.map(
              (entry) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(entry.key),
                    Text(
                      entry.value.toString(),
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
} 