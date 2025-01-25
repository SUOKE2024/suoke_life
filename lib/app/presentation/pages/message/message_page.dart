import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/message_controller.dart';

class MessagePage extends StatelessWidget {
  const MessagePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('消息'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              // TODO: 显示新建会话菜单
            },
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        if (controller.sessions.isEmpty) {
          return const Center(child: Text('暂无消息'));
        }
        return ListView.builder(
          itemCount: controller.sessions.length,
          itemBuilder: (context, index) {
            final session = controller.sessions[index];
            return ListTile(
              leading: CircleAvatar(
                backgroundImage: session.avatar != null
                    ? NetworkImage(session.avatar!)
                    : null,
                child: session.avatar == null
                    ? Text(session.title[0])
                    : null,
              ),
              title: Text(session.title),
              subtitle: Text(
                session.lastMessage ?? '',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              trailing: session.unreadCount > 0
                  ? CircleAvatar(
                      radius: 10,
                      backgroundColor: Colors.red,
                      child: Text(
                        '${session.unreadCount}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                        ),
                      ),
                    )
                  : null,
              onTap: () => controller.openChat(session),
            );
          },
        );
      }),
    );
  }
} 