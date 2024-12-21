import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/settings_controller.dart';
import 'package:suoke_life/routes/app_routes.dart';

class SettingsPage extends GetView<SettingsController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('设置'),
      ),
      body: ListView(
        children: [
          // 通用设置
          _buildSection(
            title: '通用',
            children: [
              // 主题设置
              Obx(() => ListTile(
                leading: Icon(Icons.palette),
                title: Text('主题设置'),
                subtitle: Text(_getThemeText(controller.themeMode.value)),
                trailing: Icon(Icons.chevron_right),
                onTap: () => _showThemeSelector(context),
              )),
              Divider(height: 1),
              // 语言设置
              Obx(() => ListTile(
                leading: Icon(Icons.language),
                title: Text('语言设置'),
                subtitle: Text(_getLanguageText(controller.language.value)),
                trailing: Icon(Icons.chevron_right),
                onTap: () => _showLanguageSelector(context),
              )),
            ],
          ),

          // 同步设置
          _buildSection(
            title: '同步',
            children: [
              ListTile(
                leading: Icon(Icons.sync),
                title: Text('同步设置'),
                trailing: Icon(Icons.chevron_right),
                onTap: () => Get.toNamed(AppRoutes.SYNC_SETTINGS),
              ),
            ],
          ),

          // 通知设置
          _buildSection(
            title: '通知',
            children: [
              Obx(() => SwitchListTile(
                secondary: Icon(Icons.notifications),
                title: Text('通知'),
                subtitle: Text('接收应用通知'),
                value: controller.notificationsEnabled.value,
                onChanged: controller.updateNotificationsEnabled,
              )),
              if (controller.notificationsEnabled.value) ...[
                Divider(height: 1),
                ListTile(
                  leading: Icon(Icons.notification_important),
                  title: Text('通知类型'),
                  trailing: Icon(Icons.chevron_right),
                  onTap: () => _showNotificationTypeSelector(context),
                ),
              ],
            ],
          ),

          // 隐私设置
          _buildSection(
            title: '隐私',
            children: [
              Obx(() => SwitchListTile(
                secondary: Icon(Icons.data_usage),
                title: Text('数据收集'),
                subtitle: Text('帮助改进应用体验'),
                value: controller.dataCollection.value,
                onChanged: controller.updateDataCollection,
              )),
              Divider(height: 1),
              Obx(() => SwitchListTile(
                secondary: Icon(Icons.analytics),
                title: Text('使用分析'),
                subtitle: Text('收集使用统计信息'),
                value: controller.analytics.value,
                onChanged: controller.updateAnalytics,
              )),
            ],
          ),

          // 导出设置
          _buildSection(
            title: '导出',
            children: [
              ListTile(
                leading: Icon(Icons.file_download),
                title: Text('导出设置'),
                trailing: Icon(Icons.chevron_right),
                onTap: () => Get.toNamed(AppRoutes.EXPORT),
              ),
            ],
          ),

          // 反馈
          _buildSection(
            title: '反馈',
            children: [
              ListTile(
                leading: Icon(Icons.feedback),
                title: Text('意见反馈'),
                trailing: Icon(Icons.chevron_right),
                onTap: () => Get.toNamed(AppRoutes.FEEDBACK),
              ),
              Divider(height: 1),
              ListTile(
                leading: Icon(Icons.history),
                title: Text('反馈历史'),
                trailing: Icon(Icons.chevron_right),
                onTap: () => Get.toNamed(AppRoutes.FEEDBACK_HISTORY),
              ),
            ],
          ),

          // 关于
          _buildSection(
            title: '关于',
            children: [
              ListTile(
                leading: Icon(Icons.info),
                title: Text('关于应用'),
                trailing: Icon(Icons.chevron_right),
                onTap: () => Get.toNamed(AppRoutes.ABOUT),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required List<Widget> children,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: Colors.grey[700],
            ),
          ),
        ),
        Card(
          margin: EdgeInsets.symmetric(horizontal: 16),
          child: Column(children: children),
        ),
      ],
    );
  }

  String _getThemeText(String mode) {
    switch (mode) {
      case 'light':
        return '浅色';
      case 'dark':
        return '深色';
      default:
        return '跟随系统';
    }
  }

  String _getLanguageText(String code) {
    switch (code) {
      case 'zh_CN':
        return '简体中文';
      case 'en':
        return 'English';
      default:
        return '简体中文';
    }
  }

  void _showThemeSelector(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('选择主题'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: Text('跟随系统'),
              value: 'system',
              groupValue: controller.themeMode.value,
              onChanged: (value) {
                controller.updateThemeMode(value!);
                Navigator.pop(context);
              },
            ),
            RadioListTile<String>(
              title: Text('浅色'),
              value: 'light',
              groupValue: controller.themeMode.value,
              onChanged: (value) {
                controller.updateThemeMode(value!);
                Navigator.pop(context);
              },
            ),
            RadioListTile<String>(
              title: Text('深色'),
              value: 'dark',
              groupValue: controller.themeMode.value,
              onChanged: (value) {
                controller.updateThemeMode(value!);
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showLanguageSelector(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('选择语言'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: Text('简体中文'),
              value: 'zh_CN',
              groupValue: controller.language.value,
              onChanged: (value) {
                controller.updateLanguage(value!);
                Navigator.pop(context);
              },
            ),
            RadioListTile<String>(
              title: Text('English'),
              value: 'en',
              groupValue: controller.language.value,
              onChanged: (value) {
                controller.updateLanguage(value!);
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showNotificationTypeSelector(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('通知类型'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CheckboxListTile(
              title: Text('全部通知'),
              value: controller.notificationTypes.contains('all'),
              onChanged: (value) {
                if (value!) {
                  controller.updateNotificationTypes(['all']);
                } else {
                  controller.updateNotificationTypes([]);
                }
                Navigator.pop(context);
              },
            ),
            CheckboxListTile(
              title: Text('记录提醒'),
              value: controller.notificationTypes.contains('record'),
              onChanged: (value) {
                final types = List<String>.from(controller.notificationTypes);
                if (value!) {
                  types.add('record');
                } else {
                  types.remove('record');
                }
                controller.updateNotificationTypes(types);
                Navigator.pop(context);
              },
            ),
            CheckboxListTile(
              title: Text('同步提醒'),
              value: controller.notificationTypes.contains('sync'),
              onChanged: (value) {
                final types = List<String>.from(controller.notificationTypes);
                if (value!) {
                  types.add('sync');
                } else {
                  types.remove('sync');
                }
                controller.updateNotificationTypes(types);
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }
} 