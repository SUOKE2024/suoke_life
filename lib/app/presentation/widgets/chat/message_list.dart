import 'package:flutter/material.dart';
import '../../../data/models/message.dart';
import 'message_item.dart';

class MessageList extends StatelessWidget {
  final List<Message> messages;
  final VoidCallback onLoadMore;
  final Function(Message) onMessageTap;
  final Function(Message) onMessageLongPress;

  const MessageList({
    Key? key,
    required this.messages,
    required this.onLoadMore,
    required this.onMessageTap,
    required this.onMessageLongPress,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      onNotification: (ScrollNotification scrollInfo) {
        if (scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
          onLoadMore();
        }
        return true;
      },
      child: ListView.builder(
        reverse: true,
        padding: const EdgeInsets.all(16),
        itemCount: messages.length,
        itemBuilder: (context, index) {
          final message = messages[index];
          return MessageItem(
            message: message,
            onTap: () => onMessageTap(message),
            onLongPress: () => onMessageLongPress(message),
          );
        },
      ),
    );
  }
} 