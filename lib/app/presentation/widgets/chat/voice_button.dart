import 'package:flutter/material.dart';

class VoiceButton extends StatelessWidget {
  const VoiceButton({super.key});

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.mic),
      onPressed: () {
        // TODO: 实现语音输入
      },
    );
  }
} 