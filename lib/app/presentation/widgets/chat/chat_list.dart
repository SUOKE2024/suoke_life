import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../data/models/chat_conversation.dart';
import 'chat_list_item.dart';

class ChatList extends StatelessWidget {
  final List<ChatConversation> conversations;
  final Function(ChatConversation) onTap;

  const ChatList({
    Key? key,
    required this.conversations,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      itemCount: conversations.length,
      separatorBuilder: (context, index) => const Divider(height: 1),
      itemBuilder: (context, index) {
        return ChatListItem(
          chat: conversations[index],
          onTap: () => onTap(conversations[index]),
        );
      },
    );
  }
} 