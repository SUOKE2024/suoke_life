import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/chat_detail_controller.dart';
import '../../widgets/chat/chat_message_list.dart';
import '../../widgets/chat/chat_input_bar.dart';

class ChatDetailPage extends GetView<ChatDetailController> {
  const ChatDetailPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios),
          onPressed: () => Get.back(),
        ),
        title: Row(
          children: [
            CircleAvatar(
              backgroundImage: NetworkImage(controller.conversation.avatar),
              radius: 16,
            ),
            const SizedBox(width: 8),
            Text(controller.conversation.title),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.more_horiz),
            onPressed: () => _showSettings(context),
          ),
        ],
      ),
      body: Column(
        children: [
          // 消息列表
          Expanded(
            child: ChatMessageList(
              messages: controller.messages,
              onTapAvatar: controller.onTapAvatar,
              onLongPressMessage: controller.onLongPressMessage,
            ),
          ),
          // 底部输入栏
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

  void _showSettings(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const Icon(Icons.face),
            title: const Text('形象设置'),
            onTap: () => controller.showAvatarSettings(),
          ),
          ListTile(
            leading: const Icon(Icons.record_voice_over),
            title: const Text('声音设置'),
            onTap: () => controller.showVoiceSettings(),
          ),
          ListTile(
            leading: const Icon(Icons.language),
            title: const Text('语言设置'),
            onTap: () => controller.showLanguageSettings(),
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
              icon: Icons.camera_alt,
              label: '相机',
              onTap: controller.takePhoto,
            ),
            _buildExtraAction(
              icon: Icons.photo_library,
              label: '相册',
              onTap: controller.pickImage,
            ),
            _buildExtraAction(
              icon: Icons.file_present,
              label: '文件',
              onTap: controller.pickFile,
            ),
            _buildExtraAction(
              icon: Icons.phone,
              label: '通话',
              onTap: controller.startCall,
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