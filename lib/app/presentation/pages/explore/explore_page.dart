import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/explore_controller.dart';
import '../../widgets/explore_card.dart';

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
            onPressed: () => Get.toNamed('/explore/search'),
          ),
        ],
      ),
      body: Obx(() => ListView(
        children: [
          // 知识岛探秘
          ExploreCard(
            title: '知识岛探秘',
            subtitle: '探索前沿知识',
            onTap: () => Get.toNamed('/explore/knowledge'),
          ),

          // 咖啡时光
          ExploreCard(
            title: '咖啡时光',
            subtitle: '轻松交流分享',
            onTap: () => Get.toNamed('/explore/coffee'),
          ),

          // 其他探索内容
          ...controller.exploreItems.map((item) => ExploreCard(
            title: item.title,
            subtitle: item.subtitle,
            onTap: () => Get.toNamed('/explore/detail/${item.id}'),
          )),
        ],
      )),
    );
  }
} 