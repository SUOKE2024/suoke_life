import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/explore/topic_detail_controller.dart';
import '../../widgets/explore/knowledge_graph.dart';

class TopicDetailPage extends GetView<TopicDetailController> {
  const TopicDetailPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(controller.topic.title),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: controller.shareTopic,
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 主题图片
            if (controller.topic.imageUrl != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  controller.topic.imageUrl!,
                  height: 200,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),
            const SizedBox(height: 16),
            // 主题描述
            Text(
              controller.topic.description,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 16),
            // 标签
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: controller.topic.tags.map((tag) => Chip(
                label: Text(tag),
              )).toList(),
            ),
            const SizedBox(height: 24),
            // 知识图谱
            const Text(
              '相关知识',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            KnowledgeGraph(data: controller.graphData.value),
          ],
        );
      }),
      floatingActionButton: FloatingActionButton(
        onPressed: () => controller.askLaoKe(),
        child: const Icon(Icons.chat),
      ),
    );
  }
} 