import 'package:flutter/material.dart';
import '../../../core/base/base_page.dart';
import 'chat_controller.dart';

class ChatPage extends BasePage<ChatController> {
  const ChatPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('Chat'),
      actions: [
        IconButton(
          icon: const Icon(Icons.search),
          onPressed: () => controller.searchChats(),
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Obx(() {
      if (controller.isLoading.value) {
        return const Center(child: CircularProgressIndicator());
      }
      
      if (controller.chatList.isEmpty) {
        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.chat_bubble_outline,
                size: 64,
                color: Colors.grey[400],
              ),
              const SizedBox(height: 16),
              Text(
                'No chats yet',
                style: Get.textTheme.titleMedium?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        );
      }

      return ListView.separated(
        itemCount: controller.chatList.length,
        separatorBuilder: (context, index) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final chat = controller.chatList[index];
          return ListTile(
            leading: CircleAvatar(
              backgroundImage: NetworkImage(chat.avatar),
            ),
            title: Text(chat.name),
            subtitle: Text(
              chat.lastMessage ?? '',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            trailing: chat.unreadCount > 0
              ? Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: Get.theme.colorScheme.primary,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    '${chat.unreadCount}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                    ),
                  ),
                )
              : null,
            onTap: () => controller.openChat(chat.id),
          );
        },
      );
    });
  }

  @override
  Widget? buildFloatingActionButton(BuildContext context) {
    return FloatingActionButton(
      onPressed: () => controller.startNewChat(),
      child: const Icon(Icons.add),
    );
  }
} 