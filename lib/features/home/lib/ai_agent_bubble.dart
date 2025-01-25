import 'package:flutter/material.dart';
import 'package:suoke_life/ui_components/cards/app_card.dart';

class AiAgentBubble extends StatelessWidget {
  final String message;

  const AiAgentBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: AppCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('AI Response: $message'),
          ],
        ),
      ),
    );
  }
} 