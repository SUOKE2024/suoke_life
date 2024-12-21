import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/chat_settings_controller.dart';

class ChatSettingsPage extends GetView<ChatSettingsController> {
  const ChatSettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('聊天设置'),
      ),
      body: Obx(() => ListView(
        children: [
          // 通用设置
          const ListTile(
            title: Text('通用设置'),
            dense: true,
            visualDensity: VisualDensity.compact,
          ),
          SwitchListTile(
            title: const Text('语音播报'),
            subtitle: const Text('自动播放AI回复的语音'),
            value: controller.autoPlayVoice.value,
            onChanged: controller.setAutoPlayVoice,
          ),
          SwitchListTile(
            title: const Text('震动反馈'),
            subtitle: const Text('发送消息时震动'),
            value: controller.vibrationEnabled.value,
            onChanged: controller.setVibrationEnabled,
          ),

          const Divider(),

          // 消息设置
          const ListTile(
            title: Text('消息设置'),
            dense: true,
            visualDensity: VisualDensity.compact,
          ),
          ListTile(
            title: const Text('字体大小'),
            subtitle: Text('${controller.fontSize.value.toInt()}'),
            trailing: SizedBox(
              width: 200,
              child: Slider(
                value: controller.fontSize.value,
                min: 12,
                max: 24,
                divisions: 12,
                label: '${controller.fontSize.value.toInt()}',
                onChanged: controller.setFontSize,
              ),
            ),
          ),
          SwitchListTile(
            title: const Text('显示时间'),
            subtitle: const Text('显示消息发送时间'),
            value: controller.showTimestamp.value,
            onChanged: controller.setShowTimestamp,
          ),

          const Divider(),

          // 存储设置
          const ListTile(
            title: Text('存储设置'),
            dense: true,
            visualDensity: VisualDensity.compact,
          ),
          ListTile(
            title: const Text('清空聊天记录'),
            subtitle: const Text('删除所有聊天记录'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => controller.showClearHistoryDialog(),
          ),
          SwitchListTile(
            title: const Text('自动清理'),
            subtitle: const Text('保留最近7天的聊天记录'),
            value: controller.autoCleanEnabled.value,
            onChanged: controller.setAutoCleanEnabled,
          ),
        ],
      )),
    );
  }
} 