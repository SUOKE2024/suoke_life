import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/ai/ai_settings_controller.dart';

class AISettingsPage extends GetView<AISettingsController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('AI设置'),
      ),
      body: Obx(() => ListView(
        children: [
          SwitchListTile(
            title: Text('自动回复'),
            subtitle: Text('开启后AI将自动回复消息'),
            value: controller.autoReply.value,
            onChanged: controller.setAutoReply,
          ),
          SwitchListTile(
            title: Text('语音交互'),
            subtitle: Text('开启后可以使用语音与AI对话'),
            value: controller.voiceEnabled.value,
            onChanged: controller.setVoiceEnabled,
          ),
          ListTile(
            title: Text('对话历史'),
            trailing: Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Get.toNamed('/ai/history'),
          ),
          ListTile(
            title: Text('清空对话'),
            textColor: Colors.red,
            onTap: () => controller.clearHistory(),
          ),
        ],
      )),
    );
  }
} 