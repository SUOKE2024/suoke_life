import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_colors.dart';
import 'laoke_controller.dart';

class LaokeChatPage extends GetView<LaokeController> {
  const LaokeChatPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('老克'),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () => _showAboutDialog(context),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Obx(() => ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: controller.messages.length,
              itemBuilder: (context, index) {
                final message = controller.messages[index];
                return _buildMessageBubble(message);
              },
            )),
          ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(Map<String, dynamic> message) {
    final isUser = message['isUser'] as bool;
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isUser) _buildAvatar(),
          const SizedBox(width: 8),
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isUser ? Colors.blue[100] : Colors.grey[200],
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                message['text'] as String,
                style: const TextStyle(fontSize: 16),
              ),
            ),
          ),
          const SizedBox(width: 8),
          if (isUser) _buildAvatar(isUser: true),
        ],
      ),
    );
  }

  Widget _buildAvatar({bool isUser = false}) {
    return CircleAvatar(
      backgroundColor: isUser ? Colors.blue[100] : Colors.grey[200],
      child: Icon(
        isUser ? Icons.person : Icons.smart_toy,
        color: isUser ? Colors.blue : Colors.grey[700],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
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
          Expanded(
            child: TextField(
              controller: controller.textController,
              decoration: InputDecoration(
                hintText: '输入您的问题...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.grey[100],
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
              ),
              maxLines: null,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => controller.sendMessage(),
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.send),
            onPressed: controller.sendMessage,
            color: Colors.blue,
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('关于老克'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('老克是您的知识助理，专注于：'),
            SizedBox(height: 8),
            Text('• 专业知识解答'),
            Text('• 学习方法指导'),
            Text('• 资源推荐分享'),
            Text('• 知识体系构建'),
            SizedBox(height: 16),
            Text('让我们一起探索知识的海洋！'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('了解'),
          ),
        ],
      ),
    );
  }
} 