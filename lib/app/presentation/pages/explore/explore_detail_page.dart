import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/explore_detail_controller.dart';
import '../../widgets/markdown_view.dart';

class ExploreDetailPage extends BasePage<ExploreDetailController> {
  const ExploreDetailPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: Obx(() => Text(controller.item.value.title)),
      actions: [
        IconButton(
          icon: Obx(() => Icon(
            controller.isFavorite.value
              ? Icons.favorite
              : Icons.favorite_border,
            color: controller.isFavorite.value ? Colors.red : null,
          )),
          onPressed: controller.toggleFavorite,
        ),
        IconButton(
          icon: const Icon(Icons.share_outlined),
          onPressed: controller.shareItem,
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 封面图
          AspectRatio(
            aspectRatio: 16 / 9,
            child: Obx(() => Image.network(
              controller.item.value.imageUrl,
              fit: BoxFit.cover,
            )),
          ),
          
          // 标题和描述
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Obx(() => Text(
                  controller.item.value.title,
                  style: Get.textTheme.headlineSmall,
                )),
                const SizedBox(height: 8),
                Obx(() => Text(
                  controller.item.value.description,
                  style: Get.textTheme.bodyMedium,
                )),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Icon(
                      controller.getTypeIcon(),
                      size: 16,
                      color: Colors.grey,
                    ),
                    const SizedBox(width: 4),
                    Obx(() => Text(
                      controller.item.value.type,
                      style: Get.textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                    )),
                    const SizedBox(width: 16),
                    const Icon(
                      Icons.access_time,
                      size: 16,
                      color: Colors.grey,
                    ),
                    const SizedBox(width: 4),
                    Obx(() => Text(
                      controller.getPublishDate(),
                      style: Get.textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                    )),
                  ],
                ),
              ],
            ),
          ),
          
          // 内容
          Obx(() => controller.isLoading.value
            ? const Center(child: CircularProgressIndicator())
            : Padding(
                padding: const EdgeInsets.all(16),
                child: MarkdownView(
                  data: controller.content.value,
                ),
              ),
          ),
        ],
      ),
    );
  }

  @override
  Widget? buildFloatingActionButton() {
    return FloatingActionButton(
      child: const Icon(Icons.psychology_outlined),
      onPressed: controller.showAIAssistant,
    );
  }
} 