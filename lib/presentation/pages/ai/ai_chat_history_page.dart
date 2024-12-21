import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/ai/ai_chat_history_controller.dart';
import '../../widgets/ai_chat_message.dart';
import '../../../models/message.dart';

class AIChatHistoryPage extends GetView<AIChatHistoryController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('对话历史'),
        actions: [
          IconButton(
            icon: Icon(Icons.date_range),
            onPressed: () => controller.showDatePicker(),
          ),
          IconButton(
            icon: Icon(Icons.delete_outline),
            onPressed: () => controller.showClearHistoryDialog(),
          ),
        ],
      ),
      body: Column(
        children: [
          // 日期筛选提示
          Obx(() {
            if (controller.selectedDate.value != null) {
              return Container(
                padding: EdgeInsets.all(8),
                color: Colors.grey[200],
                child: Row(
                  children: [
                    Text('显示 ${controller.formatDate(controller.selectedDate.value!)} 的对话'),
                    Spacer(),
                    IconButton(
                      icon: Icon(Icons.close, size: 16),
                      onPressed: controller.clearDateFilter,
                    ),
                  ],
                ),
              );
            }
            return SizedBox.shrink();
          }),
          
          // 消息列表
          Expanded(
            child: Obx(() {
              if (controller.isLoading.value) {
                return Center(child: CircularProgressIndicator());
              }

              if (controller.messages.isEmpty) {
                return Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.chat_bubble_outline, size: 64, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        '暂无对话记录',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                );
              }

              return ListView.builder(
                padding: EdgeInsets.all(16),
                itemCount: controller.messages.length,
                itemBuilder: (context, index) {
                  final message = controller.messages[index];
                  return Dismissible(
                    key: Key(message.id),
                    direction: DismissDirection.endToStart,
                    background: Container(
                      alignment: Alignment.centerRight,
                      padding: EdgeInsets.only(right: 16),
                      color: Colors.red,
                      child: Icon(Icons.delete, color: Colors.white),
                    ),
                    onDismissed: (_) => controller.deleteMessage(message.id),
                    child: AIChatMessage(message: message),
                  );
                },
              );
            }),
          ),
        ],
      ),
    );
  }
} 