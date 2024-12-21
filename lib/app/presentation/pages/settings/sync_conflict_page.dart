import 'package:flutter/material.dart';
import '../../core/base/base_page.dart';
import '../../controllers/sync_conflict_controller.dart';

class SyncConflictPage extends BasePage<SyncConflictController> {
  const SyncConflictPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('冲突处理'),
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Obx(() => ListView(
      children: [
        RadioListTile<String>(
          title: const Text('手动处理'),
          subtitle: const Text('发生冲突时由用户选择保留哪个版本'),
          value: '手动处理',
          groupValue: controller.selectedStrategy.value,
          onChanged: (value) => controller.updateStrategy(value!),
        ),
        RadioListTile<String>(
          title: const Text('保留本地'),
          subtitle: const Text('发生冲突时保留本地版本'),
          value: '保留本地',
          groupValue: controller.selectedStrategy.value,
          onChanged: (value) => controller.updateStrategy(value!),
        ),
        RadioListTile<String>(
          title: const Text('保留云端'),
          subtitle: const Text('发生冲突时保留云端版本'),
          value: '保留云端',
          groupValue: controller.selectedStrategy.value,
          onChanged: (value) => controller.updateStrategy(value!),
        ),
      ],
    ));
  }
} 