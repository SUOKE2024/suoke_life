import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/settings/notification_settings_controller.dart';

class NotificationSettingsPage extends StatelessWidget {
  const NotificationSettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('通知设置'),
      ),
      body: ListView(
        children: [
          // 通知总开关
          ListTile(
            title: const Text('接收通知'),
            trailing: Obx(() => Switch(
              value: controller.notificationsEnabled.value,
              onChanged: controller.toggleNotifications,
            )),
          ),

          const Divider(),

          // 通知类型设置
          const ListTile(
            title: Text('通知类型'),
            dense: true,
            enabled: false,
          ),
          ListTile(
            title: const Text('聊天消息'),
            trailing: Obx(() => Switch(
              value: controller.chatNotifications.value,
              onChanged: controller.toggleChatNotifications,
            )),
          ),
          ListTile(
            title: const Text('健康提醒'),
            trailing: Obx(() => Switch(
              value: controller.healthNotifications.value,
              onChanged: controller.toggleHealthNotifications,
            )),
          ),
          ListTile(
            title: const Text('系统通知'),
            trailing: Obx(() => Switch(
              value: controller.systemNotifications.value,
              onChanged: controller.toggleSystemNotifications,
            )),
          ),

          const Divider(),

          // 通知时间设置
          const ListTile(
            title: Text('免打扰时间'),
            dense: true,
            enabled: false,
          ),
          ListTile(
            title: const Text('开启免打扰'),
            trailing: Obx(() => Switch(
              value: controller.doNotDisturb.value,
              onChanged: controller.toggleDoNotDisturb,
            )),
          ),
          ListTile(
            title: const Text('开始时间'),
            trailing: Obx(() => Text(controller.startTime.value)),
            enabled: controller.doNotDisturb.value,
            onTap: controller.selectStartTime,
          ),
          ListTile(
            title: const Text('结束时���'),
            trailing: Obx(() => Text(controller.endTime.value)),
            enabled: controller.doNotDisturb.value,
            onTap: controller.selectEndTime,
          ),
        ],
      ),
    );
  }
} 