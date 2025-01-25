import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import '../../../domain/models/chat_info.dart';
import '../../routes/app_router.dart';

class ChatList extends StatelessWidget {
  final List<ChatInfo> chats;

  const ChatList({
    super.key,
    required this.chats,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: chats.length,
      itemBuilder: (context, index) {
        final chat = chats[index];
        return ChatListItem(chat: chat);
      },
    );
  }
}

class ChatListItem extends StatelessWidget {
  final ChatInfo chat;

  const ChatListItem({
    super.key,
    required this.chat,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundImage: chat.avatarUrl != null
            ? NetworkImage(chat.avatarUrl!)
            : null,
        child: chat.avatarUrl == null ? Text(chat.name[0]) : null,
      ),
      title: Text(chat.name),
      subtitle: chat.lastMessage != null ? Text(chat.lastMessage!) : null,
      trailing: chat.unreadCount > 0
          ? CircleAvatar(
              radius: 10,
              backgroundColor: Colors.red,
              child: Text(
                chat.unreadCount.toString(),
                style: const TextStyle(color: Colors.white, fontSize: 12),
              ),
            )
          : null,
      onTap: () {
        context.router.push(ChatDetailRoute(chatId: chat.id));
      },
    );
  }
} 