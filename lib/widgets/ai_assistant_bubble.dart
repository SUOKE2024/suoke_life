import 'package:flutter/material.dart';
import 'package:get/get.dart';

class AIAssistantBubble extends StatelessWidget {
  final String avatar;
  final VoidCallback onTap;
  final String? message;

  const AIAssistantBubble({
    Key? key,
    required this.avatar,
    required this.onTap,
    this.message,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Positioned(
      right: 16,
      bottom: 16,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (message != null)
            Container(
              margin: const EdgeInsets.only(right: 8, bottom: 8),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Text(
                message!,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[800],
                ),
              ),
            ),
          FloatingActionButton(
            onPressed: onTap,
            backgroundColor: Colors.white,
            child: CircleAvatar(
              backgroundImage: AssetImage('assets/images/ai/$avatar'),
              radius: 28,
            ),
          ),
        ],
      ),
    );
  }
} 