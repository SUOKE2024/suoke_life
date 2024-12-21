import 'package:flutter/material.dart';
import '../../core/base/base_page.dart';
import '../../../controllers/sync_settings_controller.dart';
import 'package:get/get.dart';

class SyncSettingsPage extends BasePage {
  const SyncSettingsPage({Key? key}) : super(key: key);

  @override
  String get title => '同步设置';

  @override
  Widget buildBody(BuildContext context) {
    final controller = Get.find<SyncSettingsController>();
    
    return ListView(
      children: [
        // 自动同步
        Obx(() => SwitchListTile(
          title: const Text('自动同步'),
          value: controller.autoSync.value,
          onChanged: controller.setAutoSync,
        )),
        
        // 同步范围
        ListTile(
          title: const Text('同步范围'),
          trailing: Obx(() => DropdownButton<int>(
            value: controller.syncRange.value,
            items: const [
              DropdownMenuItem(value: 7, child: Text('最近7天')),
              DropdownMenuItem(value: 30, child: Text('最近30天')),
              DropdownMenuItem(value: 90, child: Text('最近90天')),
              DropdownMenuItem(value: -1, child: Text('全部')),
            ],
            onChanged: (value) => controller.setSyncRange(value ?? 7),
          )),
        ),
      ],
    );
  }
} 