import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ChatAssistantsPage extends StatelessWidget {
  const ChatAssistantsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const CircleAvatar(
              child: Icon(Icons.smart_toy),
            ),
            title: const Text('小艾'),
            subtitle: const Text('生活管家'),
            onTap: () => Get.toNamed('/chat/xiaoi'),
          ),
          ListTile(
            leading: const CircleAvatar(
              child: Icon(Icons.psychology),
            ),
            title: const Text('老克'),
            subtitle: const Text('知识顾问'),
            onTap: () => Get.toNamed('/chat/oldke'),
          ),
          ListTile(
            leading: const CircleAvatar(
              child: Icon(Icons.business),
            ),
            title: const Text('小克'),
            subtitle: const Text('商务助手'),
            onTap: () => Get.toNamed('/chat/xiaoke'),
          ),
        ],
      ),
    );
  }
} 