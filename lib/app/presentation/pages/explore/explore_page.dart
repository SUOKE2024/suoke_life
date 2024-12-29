import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/explore/explore_controller.dart';
import '../../widgets/explore/topic_card.dart';
import '../../widgets/explore/knowledge_graph.dart';

class ExplorePage extends GetView<ExploreController> {
  const ExplorePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('探索'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => controller.showSearch(),
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
            // 知识图谱
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '知识图谱',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    KnowledgeGraph(data: controller.graphData.value),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            // 探索主题
            const Text(
              '探索主题',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                childAspectRatio: 1.2,
              ),
              itemCount: controller.topics.length,
              itemBuilder: (context, index) {
                final topic = controller.topics[index];
                return TopicCard(
                  topic: topic,
                  onTap: () => controller.openTopic(topic),
                );
              },
            ),
          ],
        );
      }),
      floatingActionButton: FloatingActionButton(
        onPressed: () => controller.showLaoKe(),
        child: const Icon(Icons.chat),
      ),
    );
  }
} 