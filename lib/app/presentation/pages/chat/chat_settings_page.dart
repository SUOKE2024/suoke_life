import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ChatSettingsPage extends StatelessWidget {
  const ChatSettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const Icon(Icons.person),
            title: const Text('查看资料'),
            onTap: () => Get.back(),
          ),
          ListTile(
            leading: const Icon(Icons.volume_up),
            title: const Text('声音设置'),
            onTap: () => Get.back(),
          ),
        ],
      ),
    );
  }
} 