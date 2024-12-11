import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../models/chat_message.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  final VoidCallback? onRetry;

  const ChatBubble({
    Key? key,
    required this.message,
    this.onRetry,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == MessageRole.user;
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) _buildAvatar(),
          const SizedBox(width: 8),
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isUser ? AppColors.chatBubbleUser : AppColors.chatBubbleBot,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    message.content,
                    style: TextStyle(
                      color: isUser ? AppColors.chatTextUser : AppColors.chatTextBot,
                    ),
                  ),
                  if (message.isError && onRetry != null) ...[
                    const SizedBox(height: 8),
                    GestureDetector(
                      onTap: onRetry,
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.refresh,
                            size: 16,
                            color: AppColors.error,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '重试',
                            style: TextStyle(
                              color: AppColors.error,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(width: 8),
          if (isUser) _buildAvatar(),
        ],
      ),
    );
  }

  Widget _buildAvatar() {
    return CircleAvatar(
      radius: 16,
      backgroundColor: message.role == MessageRole.user ? AppColors.primary : AppColors.secondary,
      child: Icon(
        message.role == MessageRole.user ? Icons.person : Icons.smart_toy,
        size: 20,
        color: Colors.white,
      ),
    );
  }
} 