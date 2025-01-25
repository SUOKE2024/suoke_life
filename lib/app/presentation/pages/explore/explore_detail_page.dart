import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/explore/explore_detail_controller.dart';

class ExploreDetailPage extends StatelessWidget {
  const ExploreDetailPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(controller.item.title),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: controller.shareItem,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题
            Text(
              controller.item.title,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),

            // 内容
            Text(
              controller.item.content,
              style: const TextStyle(
                fontSize: 16,
                height: 1.6,
              ),
            ),

            const SizedBox(height: 32),

            // 相关推荐
            const Text(
              '相关推荐',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Obx(() => ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: controller.relatedItems.length,
              itemBuilder: (context, index) {
                final item = controller.relatedItems[index];
                return ListTile(
                  title: Text(item.title),
                  subtitle: Text(
                    item.content,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  onTap: () => controller.onRelatedItemTap(item),
                );
              },
            )),
          ],
        ),
      ),
    );
  }
} 