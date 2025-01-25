import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/login_history_controller.dart';
import '../../widgets/login_record_item.dart';

class LoginHistoryPage extends BasePage<LoginHistoryController> {
  const LoginHistoryPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('登录历史'),
      actions: [
        IconButton(
          icon: const Icon(Icons.filter_list),
          onPressed: controller.showFilterOptions,
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Column(
      children: [
        // 筛选条件
        Obx(() => Container(
          padding: const EdgeInsets.all(16),
          color: Get.theme.cardColor,
          child: Row(
            children: [
              const Icon(Icons.filter_alt_outlined, size: 20),
              const SizedBox(width: 8),
              Text(
                '筛选: ${controller.currentFilter.value}',
                style: const TextStyle(fontSize: 14),
              ),
              const Spacer(),
              Text(
                '共 ${controller.records.length} 条记录',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        )),

        // 登录记录列表
        Expanded(
          child: Obx(() {
            if (controller.isLoading.value) {
              return const Center(child: CircularProgressIndicator());
            }

            if (controller.records.isEmpty) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.history,
                      size: 64,
                      color: Colors.grey[400],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      '暂无登录记录',
                      style: Get.textTheme.titleMedium?.copyWith(
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              );
            }

            return RefreshIndicator(
              onRefresh: controller.refreshRecords,
              child: ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: controller.records.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final record = controller.records[index];
                  return LoginRecordItem(
                    record: record,
                    onTap: () => controller.showRecordDetail(record),
                  );
                },
              ),
            );
          }),
        ),
      ],
    );
  }
} 