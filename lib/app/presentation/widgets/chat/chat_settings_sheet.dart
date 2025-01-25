import 'package:flutter/material.dart';

class ChatSettingsSheet extends StatelessWidget {
  const ChatSettingsSheet({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        ListTile(
          leading: const Icon(Icons.person),
          title: const Text('查看资料'),
          onTap: () {
            // TODO: 实现查看资料
            Navigator.pop(context);
          },
        ),
        ListTile(
          leading: const Icon(Icons.delete),
          title: const Text('清空聊天记录'),
          onTap: () {
            // TODO: 实现清空聊天记录
            Navigator.pop(context);
          },
        ),
      ],
    );
  }
} 