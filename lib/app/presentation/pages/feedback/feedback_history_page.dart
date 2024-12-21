import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/feedback_history_controller.dart';
import '../../widgets/feedback_history_item.dart';

class FeedbackHistoryPage extends BasePage<FeedbackHistoryController> {
  const FeedbackHistoryPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('反馈历史'),
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
                '${controller.selectedStatus.value} · ${controller.selectedType.value}',
                style: Get.textTheme.bodyMedium,
              ),
              const Spacer(),
              TextButton(
                onPressed: controller.resetFilter,
                child: const Text('重置'),
              ),
            ],
          ),
        )),

        // 反馈列表
        Expanded(
          child: Obx(() {
            if (controller.isLoading.value) {
              return const Center(child: CircularProgressIndicator());
            }

            if (controller.feedbacks.isEmpty) {
              return Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.feedback_outlined,
                      size: 64,
                      color: Colors.grey[400],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      '暂无反馈记录',
                      style: Get.textTheme.titleMedium?.copyWith(
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              );
            }

            return RefreshIndicator(
              onRefresh: controller.refreshFeedbacks,
              child: ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: controller.feedbacks.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final feedback = controller.feedbacks[index];
                  return FeedbackHistoryItem(
                    feedback: feedback,
                    onTap: () => controller.showFeedbackDetail(feedback),
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