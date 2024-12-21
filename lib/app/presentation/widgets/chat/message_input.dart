import 'package:flutter/material.dart';
import 'package:get/get.dart';

class MessageInput extends StatelessWidget {
  final TextEditingController controller;
  final Function(String) onSendText;
  final Function(String) onSendVoice;
  final Function(String) onSendImage;
  final Function(String) onSendFile;

  const MessageInput({
    Key? key,
    required this.controller,
    required this.onSendText,
    required this.onSendVoice,
    required this.onSendImage,
    required this.onSendFile,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            // 语音按钮
            IconButton(
              icon: const Icon(Icons.mic),
              onPressed: () {
                // 实现语音录制
              },
            ),
            // 文本输入框
            Expanded(
              child: TextField(
                controller: controller,
                decoration: const InputDecoration(
                  hintText: '输入消息...',
                  border: InputBorder.none,
                ),
                maxLines: 5,
                minLines: 1,
              ),
            ),
            // 表情按钮
            IconButton(
              icon: const Icon(Icons.emoji_emotions_outlined),
              onPressed: () {
                // 显示表情面板
              },
            ),
            // 更多功能按钮
            IconButton(
              icon: const Icon(Icons.add_circle_outline),
              onPressed: () => _showMoreOptions(context),
            ),
            // 发送按钮
            ValueBuilder<TextEditingController?>(
              builder: (controller, updater) => IconButton(
                icon: const Icon(Icons.send),
                onPressed: controller?.text.isEmpty == true
                    ? null
                    : () => onSendText(controller?.text ?? ''),
              ),
              initialValue: controller,
              onUpdate: (value) => controller,
              onDispose: (value) => null,
            ),
          ],
        ),
      ),
    );
  }

  void _showMoreOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.symmetric(vertical: 20),
        child: Wrap(
          alignment: WrapAlignment.spaceEvenly,
          children: [
            _buildOptionItem(
              icon: Icons.image,
              label: '图片',
              onTap: () {
                Get.back();
                // 选择图片
              },
            ),
            _buildOptionItem(
              icon: Icons.camera_alt,
              label: '拍照',
              onTap: () {
                Get.back();
                // 打开相机
              },
            ),
            _buildOptionItem(
              icon: Icons.file_copy,
              label: '文件',
              onTap: () {
                Get.back();
                // 选择文件
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOptionItem({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 80,
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Column(
          children: [
            Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                color: Colors.blue[100],
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: Colors.blue),
            ),
            const SizedBox(height: 8),
            Text(label),
          ],
        ),
      ),
    );
  }
} 