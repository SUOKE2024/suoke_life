import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/settings_controller.dart';

class SyncRangePage extends GetView<SettingsController> {
  final _syncRanges = [
    {
      'key': 'life_records',
      'title': '生活记录',
      'subtitle': '包括记录内容、标签和图片',
    },
    {
      'key': 'tags',
      'title': '标签管理',
      'subtitle': '标签分类和设置',
    },
    {
      'key': 'settings',
      'title': '应用设置',
      'subtitle': '主题、语言等基本设置',
    },
    {
      'key': 'feedback',
      'title': '反馈记录',
      'subtitle': '用户反馈和回复记录',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('同步范围'),
      ),
      body: ListView.builder(
        itemCount: _syncRanges.length,
        itemBuilder: (context, index) {
          final item = _syncRanges[index];
          return Obx(() => SwitchListTile(
            title: Text(item['title']!),
            subtitle: Text(item['subtitle']!),
            value: controller.isSyncEnabled(item['key']!),
            onChanged: (enabled) => controller.updateSyncRange(item['key']!, enabled),
          ));
        },
      ),
    );
  }
} 