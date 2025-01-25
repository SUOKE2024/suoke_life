import 'package:flutter/material.dart';
import 'package:get/get.dart';

class AIChatCard extends StatelessWidget {
  const AIChatCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: () => Navigator.pushNamed('/ai/chat'),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.smart_toy),
                  const SizedBox(width: 8),
                  const Text(
                    'AI助手',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () => Navigator.pushNamed('/ai/settings'),
                    child: const Text('设置'),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text('有什么可以帮你的吗？'),
            ],
          ),
        ),
      ),
    );
  }
} 