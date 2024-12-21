import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/chat_controller.dart';
import 'package:suoke_life/routes/app_routes.dart';

class ChatPage extends GetView<ChatController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Obx(() => Text(controller.title)),
      ),
      body: ListView.builder(
        itemCount: 10,
        itemBuilder: (context, index) {
          return ListTile(
            leading: CircleAvatar(
              child: Text('${index + 1}'),
            ),
            title: Text('聊天 ${index + 1}'),
            subtitle: Text('最新消息 ${index + 1}'),
            onTap: () => Get.toNamed(
              AppRoutes.CHAT_DETAIL,
              arguments: {'chatId': index},
            ),
          );
        },
      ),
    );
  }
} 