import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/explore_controller.dart';
import 'package:suoke_life/routes/app_routes.dart';

class ExplorePage extends GetView<ExploreController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('探索'),
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          _buildExploreSection(
            title: '文化探索',
            items: [
              ExploreItem(
                icon: Icons.school,
                title: '知识岛',
                route: AppRoutes.KNOWLEDGE_ISLAND,
              ),
              ExploreItem(
                icon: Icons.coffee,
                title: '咖啡时光',
                route: AppRoutes.COFFEE_TIME,
              ),
            ],
          ),
          _buildExploreSection(
            title: '美食探索',
            items: [
              ExploreItem(
                icon: Icons.restaurant,
                title: '美食探店',
                route: AppRoutes.FOOD_EXPLORE,
              ),
              ExploreItem(
                icon: Icons.spa,
                title: '菌食记',
                route: AppRoutes.MUSHROOM_NOTES,
              ),
            ],
          ),
          _buildExploreSection(
            title: '生活探索',
            items: [
              ExploreItem(
                icon: Icons.local_florist,
                title: '花之物语',
                route: AppRoutes.FLOWER_STORY,
              ),
              ExploreItem(
                icon: Icons.house,
                title: '寻宿雅居',
                route: AppRoutes.STAY_SEARCH,
              ),
              ExploreItem(
                icon: Icons.place,
                title: '网红打卡',
                route: AppRoutes.POPULAR_SPOTS,
              ),
            ],
          ),
          _buildExploreSection(
            title: '游戏探索',
            items: [
              ExploreItem(
                icon: Icons.games,
                title: '老克寻宝',
                route: AppRoutes.TREASURE_GAME,
              ),
            ],
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        child: CircleAvatar(
          backgroundImage: AssetImage('assets/images/avatars/lao_ke.png'),
        ),
        onPressed: controller.onAIAssistantTap,
      ),
    );
  }

  Widget _buildExploreSection({
    required String title,
    required List<ExploreItem> items,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.symmetric(vertical: 8),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        GridView.count(
          shrinkWrap: true,
          physics: NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          childAspectRatio: 1.5,
          children: items.map((item) => _buildExploreCard(item)).toList(),
        ),
        SizedBox(height: 16),
      ],
    );
  }

  Widget _buildExploreCard(ExploreItem item) {
    return Card(
      child: InkWell(
        onTap: () => Get.toNamed(item.route),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(item.icon, size: 32),
            SizedBox(height: 8),
            Text(item.title),
          ],
        ),
      ),
    );
  }
}

class ExploreItem {
  final IconData icon;
  final String title;
  final String route;

  ExploreItem({
    required this.icon,
    required this.title,
    required this.route,
  });
} 