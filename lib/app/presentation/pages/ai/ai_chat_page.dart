import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/ai_chat_controller.dart';
import '../../widgets/chat/chat_message_list.dart';
import '../../widgets/chat/chat_input_bar.dart';
import '../../../core/config/doubao_config.dart';

class AiChatPage extends GetView<AiChatController> {
  const AiChatPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: buildAppBar(),
      body: Column(
        children: [
          Expanded(
            child: Obx(() => ChatMessageList(
              messages: controller.messages,
              onTapAvatar: controller.onTapAvatar,
              onLongPressMessage: controller.onLongPressMessage,
            )),
          ),
          ChatInputBar(
            onSendText: controller.sendTextMessage,
            onVoiceStart: controller.startVoiceRecord,
            onVoiceEnd: controller.stopVoiceRecord,
            onVoiceCancel: controller.cancelVoiceRecord,
            onTapExtra: () => _showExtraActions(context),
          ),
        ],
      ),
    );
  }

  AppBar buildAppBar() {
    return AppBar(
      title: Obx(() => Row(
        children: [
          CircleAvatar(
            backgroundImage: AssetImage(controller.conversation.avatar),
            radius: 16,
          ),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(controller.conversation.title),
              Text(
                _getAiType(controller.selectedModel.value),
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ],
      )),
      actions: [
        PopupMenuButton<String>(
          onSelected: controller.changeModel,
          itemBuilder: (context) => DouBaoConfig.models.entries.map((entry) {
            return PopupMenuItem<String>(
              value: entry.key,
              child: Row(
                children: [
                  Image.asset(
                    'assets/images/${entry.key}_avatar.png',
                    width: 24,
                    height: 24,
                  ),
                  const SizedBox(width: 8),
                  Text(entry.value),
                ],
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  String _getAiType(String model) {
    switch (model) {
      case 'xiaoai':
        return '生活管家';
      case 'laoke':
        return '知识顾问';
      case 'xiaoke':
        return '商务助手';
      default:
        return 'AI助手';
    }
  }

  void _showSettings(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const Icon(Icons.smart_toy),
            title: const Text('助手设置'),
            onTap: () {
              Get.back();
              controller.showAssistantSettings();
            },
          ),
          ListTile(
            leading: const Icon(Icons.record_voice_over),
            title: const Text('语音设置'),
            onTap: () {
              Get.back();
              controller.showVoiceSettings();
            },
          ),
          ListTile(
            leading: const Icon(Icons.language),
            title: const Text('语言设置'),
            onTap: () {
              Get.back();
              controller.showLanguageSettings();
            },
          ),
        ],
      ),
    );
  }

  void _showExtraActions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 20),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildExtraAction(
              icon: Icons.image,
              label: '图片',
              onTap: () {
                Get.back();
                controller.pickImage();
              },
            ),
            _buildExtraAction(
              icon: Icons.mic,
              label: '语音',
              onTap: () {
                Get.back();
                controller.startVoiceRecord();
              },
            ),
            _buildExtraAction(
              icon: Icons.file_present,
              label: '文件',
              onTap: () {
                Get.back();
                controller.pickFile();
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExtraAction({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon),
          ),
          const SizedBox(height: 8),
          Text(label),
        ],
      ),
    );
  }
} 