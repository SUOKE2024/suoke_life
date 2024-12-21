import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/chat/chat_settings_controller.dart';
import '../../../routes/app_routes.dart';

class ChatSettingsPage extends GetView<ChatSettingsController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('聊天设置'),
      ),
      body: Obx(() => ListView(
        children: [
          SwitchListTile(
            title: Text('消息通知'),
            value: controller.notificationsEnabled.value,
            onChanged: controller.setNotificationsEnabled,
          ),
          SwitchListTile(
            title: Text('声音提醒'),
            value: controller.soundEnabled.value,
            onChanged: controller.setSoundEnabled,
          ),
          ListTile(
            title: Text('聊天记录'),
            trailing: Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Get.toNamed(AppRoutes.CHAT_HISTORY),
          ),
          ListTile(
            title: Text('清空聊天记录'),
            textColor: Colors.red,
            onTap: () => controller.clearChatHistory(),
          ),
        ],
      )),
    );
  }
} 