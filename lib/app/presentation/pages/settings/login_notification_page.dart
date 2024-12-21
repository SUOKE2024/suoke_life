import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/login_notification_controller.dart';

class LoginNotificationPage extends BasePage<LoginNotificationController> {
  const LoginNotificationPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('登录通知设置'),
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // 通知开关
        Card(
          child: Column(
            children: [
              ListTile(
                title: const Text('登录通知'),
                subtitle: const Text('新设备登录时通知'),
                trailing: Obx(() => Switch(
                  value: controller.notificationEnabled.value,
                  onChanged: controller.toggleNotification,
                )),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 通知方式
        Obx(() {
          if (!controller.notificationEnabled.value) {
            return const SizedBox();
          }
          return Card(
            child: Column(
              children: [
                ListTile(
                  title: const Text('通知方式'),
                  subtitle: const Text('选择接收通知的方式'),
                ),
                const Divider(height: 1),
                ListTile(
                  title: const Text('应用内通知'),
                  trailing: Obx(() => Switch(
                    value: controller.inAppNotification.value,
                    onChanged: controller.toggleInAppNotification,
                  )),
                ),
                const Divider(height: 1),
                ListTile(
                  title: const Text('邮件通知'),
                  trailing: Obx(() => Switch(
                    value: controller.emailNotification.value,
                    onChanged: controller.toggleEmailNotification,
                  )),
                ),
                const Divider(height: 1),
                ListTile(
                  title: const Text('短信通知'),
                  trailing: Obx(() => Switch(
                    value: controller.smsNotification.value,
                    onChanged: controller.toggleSmsNotification,
                  )),
                ),
              ],
            ),
          );
        }),

        const SizedBox(height: 16),

        // 通知场景
        Obx(() {
          if (!controller.notificationEnabled.value) {
            return const SizedBox();
          }
          return Card(
            child: Column(
              children: [
                ListTile(
                  title: const Text('通知场景'),
                  subtitle: const Text('选择需要通知的登录场景'),
                ),
                const Divider(height: 1),
                ListTile(
                  title: const Text('新设备登录'),
                  trailing: Obx(() => Switch(
                    value: controller.newDeviceNotification.value,
                    onChanged: controller.toggleNewDeviceNotification,
                  )),
                ),
                const Divider(height: 1),
                ListTile(
                  title: const Text('异地登录'),
                  trailing: Obx(() => Switch(
                    value: controller.unusualLocationNotification.value,
                    onChanged: controller.toggleUnusualLocationNotification,
                  )),
                ),
                const Divider(height: 1),
                ListTile(
                  title: const Text('异常时间登录'),
                  subtitle: const Text('非常用时间段登录'),
                  trailing: Obx(() => Switch(
                    value: controller.unusualTimeNotification.value,
                    onChanged: controller.toggleUnusualTimeNotification,
                  )),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
} 