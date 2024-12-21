import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/chat/chat_history_controller.dart';
import 'package:suoke_life/widgets/chat_message.dart';

class ChatHistoryPage extends GetView<ChatHistoryController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('聊天记录'),
        actions: [
          IconButton(
            icon: Icon(Icons.date_range),
            onPressed: () => controller.showDatePicker(),
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return Center(child: CircularProgressIndicator());
        }
        
        if (controller.messages.isEmpty) {
          return Center(child: Text('暂无聊天记录'));
        }
        
        return ListView.builder(
          padding: EdgeInsets.all(16),
          itemCount: controller.messages.length,
          itemBuilder: (context, index) {
            final message = controller.messages[index];
            return ChatMessage(
              message: message,
              avatar: controller.chatAvatar,
            );
          },
        );
      }),
    );
  }
} 