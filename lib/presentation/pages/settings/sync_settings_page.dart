import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/settings_controller.dart';
import 'package:suoke_life/routes/app_routes.dart';
import 'package:suoke_life/app/core/widgets/sync_progress_indicator.dart';

class SyncSettingsPage extends GetView<SettingsController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('同步设置'),
      ),
      body: ListView(
        children: [
          // 自动同步开关
          Obx(() => SwitchListTile(
            title: Text('自动同步'),
            subtitle: Text('开启后将自动同步数据'),
            value: controller.autoSync.value,
            onChanged: (enabled) => controller.updateAutoSync(enabled),
          )),

          // 仅WIFI同步
          Obx(() => SwitchListTile(
            title: Text('仅在WIFI下同步'),
            subtitle: Text('开启后仅在WIFI网络下同步数据'),
            value: controller.wifiOnlySync.value,
            onChanged: controller.autoSync.value 
                ? (enabled) => controller.updateWifiOnlySync(enabled)
                : null,
          )),

          Divider(height: 32),

          // 同步范围设置
          ListTile(
            title: Text('同步范围'),
            subtitle: Text('选择需要同步的数据类型'),
            trailing: Icon(Icons.chevron_right),
            onTap: () => Get.toNamed(AppRoutes.SYNC_RANGE),
          ),

          Divider(height: 32),

          // 同步日志
          ListTile(
            title: Text('同步日志'),
            subtitle: Text('查看同步历史记录'),
            trailing: Icon(Icons.chevron_right),
            onTap: () => Get.toNamed(AppRoutes.SYNC_LOGS),
          ),

          // 同步冲突
          Obx(() {
            final hasConflicts = controller.hasUnresolvedConflicts.value;
            return ListTile(
              title: Text('同步冲突'),
              subtitle: Text(hasConflicts ? '有未解决的冲突' : '暂无冲突'),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (hasConflicts)
                    Container(
                      margin: EdgeInsets.only(right: 8),
                      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.red,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '!',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  Icon(Icons.chevron_right),
                ],
              ),
              onTap: () => Get.toNamed(AppRoutes.SYNC_CONFLICTS),
            );
          }),

          Divider(height: 32),

          // 立即同步按钮
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ElevatedButton(
              onPressed: () {
                // TODO: 实现立即同步功能
                Get.snackbar('提示', '开始同步数据...');
              },
              child: Text('立即同步'),
            ),
          ),

          // 上次同步时间
          Padding(
            padding: EdgeInsets.all(16),
            child: Text(
              '上次同步时间：2024-03-20 15:30',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }
} 