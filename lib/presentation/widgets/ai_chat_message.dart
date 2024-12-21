import 'package:flutter/material.dart';
import '../../models/message.dart';

class AIChatMessage extends StatelessWidget {
  final Message message;

  const AIChatMessage({
    Key? key,
    required this.message,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isUser = message.isFromUser;
    
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 8,
      ),
      child: Row(
        mainAxisAlignment: isUser 
            ? MainAxisAlignment.end 
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) _buildAvatar(),
          const SizedBox(width: 8),
          Flexible(
            child: Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isUser 
                    ? Theme.of(context).primaryColor
                    : Colors.grey[200],
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                message.content,
                style: TextStyle(
                  color: isUser ? Colors.white : Colors.black,
                ),
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
      backgroundImage: AssetImage(
        message.isFromUser 
            ? 'assets/images/user_avatar.png'
            : 'assets/images/ai/xiaoi.png',
      ),
    );
  }
} 