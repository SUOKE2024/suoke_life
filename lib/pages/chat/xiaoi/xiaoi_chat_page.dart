import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_colors.dart';
import '../../../models/chat_message.dart';
import '../widgets/chat_bubble.dart';
import 'xiaoi_controller.dart';

class XiaoiChatPage extends GetView<XiaoiController> {
  const XiaoiChatPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Text('小艾'),
            Text(
              '您的AI健康助手',
              style: TextStyle(fontSize: 12),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.mic),
            onPressed: () {
              // TODO: 语音设置
              Get.snackbar('提示', '语音设置功能开发中...');
            },
            tooltip: '语音设置',
          ),
          IconButton(
            icon: const Icon(Icons.volume_up),
            onPressed: () {
              // TODO: 扬声器设置
              Get.snackbar('提示', '扬声器设置功能开发中...');
            },
            tooltip: '扬声器设置',
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: 进入设置页面
              Get.snackbar('提示', '设置功能开发中...');
            },
            tooltip: '设置',
          ),
        ],
      ),
      body: Column(
        children: [
          // 聊天消息列表
          Expanded(
            child: Obx(
              () => ListView.builder(
                padding: const EdgeInsets.all(16),
                reverse: true,
                itemCount: controller.messages.length,
                itemBuilder: (context, index) {
                  final message = controller.messages[index];
                  return ChatBubble(
                    message: message,
                    onRetry: message.isError
                        ? () => controller.sendTextMessage(message.content)
                        : null,
                  );
                },
              ),
            ),
          ),
          
          // 输入区域
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.mic),
            onPressed: () {
              // TODO: 语音输入
              Get.snackbar('提示', '语音输入功能开发中...');
            },
          ),
          Expanded(
            child: TextField(
              decoration: const InputDecoration(
                hintText: '输入消息...',
                border: InputBorder.none,
              ),
              onSubmitted: controller.sendTextMessage,
            ),
          ),
          IconButton(
            icon: const Icon(Icons.send),
            color: AppColors.primary,
            onPressed: () {
              // TODO: 发送消息
              Get.snackbar('提示', '请按回车键发送消息');
            },
          ),
        ],
      ),
    );
  }
} 