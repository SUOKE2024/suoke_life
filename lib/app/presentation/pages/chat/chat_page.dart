import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/chat/chat_controller.dart';
import '../../widgets/chat/chat_list.dart';

class ChatPage extends GetView<ChatController> {
  const ChatPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('消息'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              // 显示添加菜单
              showModalBottomSheet(
                context: context,
                builder: (context) => Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    ListTile(
                      leading: const Icon(Icons.person_add),
                      title: const Text('添加朋友'),
                      onTap: () {
                        Navigator.pop(context);
                        // TODO: 实现添加朋友功能
                      },
                    ),
                    ListTile(
                      leading: const Icon(Icons.group_add),
                      title: const Text('发起群聊'),
                      onTap: () {
                        Navigator.pop(context);
                        // TODO: 实现发起群聊功能
                      },
                    ),
                    ListTile(
                      leading: const Icon(Icons.calendar_today),
                      title: const Text('预约咨询'),
                      onTap: () {
                        Navigator.pop(context);
                        // TODO: 实现预约咨询功能
                      },
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      body: GetBuilder<ChatController>(
        builder: (_) => ChatList(
          messages: controller.messages,
          onTap: (roomId) => Get.toNamed('/chat/detail', arguments: roomId),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // 显示 AI 助手选择界面
          showModalBottomSheet(
            context: context,
            builder: (context) => Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ListTile(
                  leading: const CircleAvatar(child: Text('小艾')),
                  title: const Text('小艾'),
                  subtitle: const Text('生活服务助手'),
                  onTap: () {
                    Navigator.pop(context);
                    Get.toNamed('/chat/xiaoi');
                  },
                ),
                ListTile(
                  leading: const CircleAvatar(child: Text('老克')),
                  title: const Text('老克'),
                  subtitle: const Text('知识探索助手'),
                  onTap: () {
                    Navigator.pop(context);
                    Get.toNamed('/chat/laoke');
                  },
                ),
                ListTile(
                  leading: const CircleAvatar(child: Text('小克')),
                  title: const Text('小克'),
                  subtitle: const Text('商务助手'),
                  onTap: () {
                    Navigator.pop(context);
                    Get.toNamed('/chat/xiaoke');
                  },
                ),
              ],
            ),
          );
        },
        child: const Icon(Icons.chat),
      ),
    );
  }
} 