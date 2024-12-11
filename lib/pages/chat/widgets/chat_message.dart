import 'package:flutter/material.dart';
import '../models/message.dart';

class ChatMessage extends StatelessWidget {
  final Message message;
  final VoidCallback? onPlayVoice;

  const ChatMessage({
    Key? key,
    required this.message,
    this.onPlayVoice,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) _buildAvatar(),
          const SizedBox(width: 8),
          _buildMessageContent(context),
          const SizedBox(width: 8),
          if (isUser) _buildAvatar(),
        ],
      ),
    );
  }

  Widget _buildAvatar() {
    return CircleAvatar(
      backgroundColor: message.isUser ? Colors.blue : Colors.green,
      child: Icon(
        message.isUser ? Icons.person : Icons.smart_toy,
        color: Colors.white,
      ),
    );
  }

  Widget _buildMessageContent(BuildContext context) {
    return Flexible(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: message.isUser ? Colors.blue.shade100 : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(16),
        ),
        child: _buildMessageByType(context),
      ),
    );
  }

  Widget _buildMessageByType(BuildContext context) {
    switch (message.type) {
      case MessageType.text:
        return Text(message.content);
      
      case MessageType.voice:
        return InkWell(
          onTap: onPlayVoice,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.play_arrow),
              const SizedBox(width: 8),
              Text('${message.duration?.inSeconds ?? 0}秒'),
            ],
          ),
        );
      
      case MessageType.image:
        return Image.network(
          message.content,
          fit: BoxFit.cover,
          loadingBuilder: (context, child, loadingProgress) {
            if (loadingProgress == null) return child;
            return const CircularProgressIndicator();
          },
        );
      
      case MessageType.video:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            AspectRatio(
              aspectRatio: 16 / 9,
              child: Container(
                color: Colors.black,
                child: const Center(
                  child: Icon(
                    Icons.play_circle_outline,
                    color: Colors.white,
                    size: 48,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 4),
            const Text('视频通话记录'),
          ],
        );

      case MessageType.file:
        return InkWell(
          onTap: () {
            // TODO: 打开文件
          },
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.file_present),
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  message.fileName ?? '未知文件',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        );
    }
  }
}
