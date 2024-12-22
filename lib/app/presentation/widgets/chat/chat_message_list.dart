import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../data/models/chat_message.dart';
import '../../../core/theme/app_colors.dart';

class ChatMessageList extends StatelessWidget {
  final List<ChatMessage> messages;
  final Function(ChatMessage) onLongPress;
  final Function(String) onTapAvatar;

  const ChatMessageList({
    Key? key,
    required this.messages,
    required this.onLongPress,
    required this.onTapAvatar,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      reverse: true,
      padding: const EdgeInsets.all(16),
      itemCount: messages.length,
      itemBuilder: (context, index) {
        final message = messages[index];
        return _buildMessageItem(message);
      },
    );
  }

  Widget _buildMessageItem(ChatMessage message) {
    final isFromUser = message.isFromUser;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: isFromUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isFromUser) ...[
            GestureDetector(
              onTap: () => onTapAvatar(message.senderId),
              child: CircleAvatar(
                backgroundImage: AssetImage(message.senderAvatar),
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: GestureDetector(
              onLongPress: () => onLongPress(message),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isFromUser ? AppColors.primary : Colors.grey[200],
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  message.content,
                  style: TextStyle(
                    color: isFromUser ? Colors.white : Colors.black,
                  ),
                ),
              ),
            ),
          ),
          if (isFromUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              backgroundImage: AssetImage(message.senderAvatar),
            ),
          ],
        ],
      ),
    );
  }
} 