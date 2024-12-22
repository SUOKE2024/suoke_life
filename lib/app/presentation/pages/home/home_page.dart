import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/home_controller.dart';
import '../../widgets/chat/chat_list_item.dart';

class HomePage extends GetView<HomeController> {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('聊天'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => controller.createNewChat(),
          ),
        ],
      ),
      body: Obx(() => ListView.builder(
        itemCount: controller.conversations.length,
        itemBuilder: (context, index) {
          final chat = controller.conversations[index];
          return ChatListItem(
            chat: chat,
            onTap: () => controller.openChat(chat),
          );
        },
      )),
    );
  }
} 