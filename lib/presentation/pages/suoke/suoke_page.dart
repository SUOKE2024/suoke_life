import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/suoke_controller.dart';
import 'package:suoke_life/routes/app_routes.dart';

class SuokePage extends GetView<SuokeController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('SUOKE'),
      ),
      body: GridView.count(
        crossAxisCount: 2,
        padding: EdgeInsets.all(16),
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        children: [
          _buildServiceCard(
            icon: Icons.health_and_safety,
            title: '健康问卷',
            onTap: () => Get.toNamed(AppRoutes.HEALTH_SURVEY),
          ),
          _buildServiceCard(
            icon: Icons.spa,
            title: '中医体质检测',
            onTap: () => Get.toNamed(AppRoutes.TCM_TEST),
          ),
          _buildServiceCard(
            icon: Icons.shopping_basket,
            title: '农产品定制',
            onTap: () => Get.toNamed(AppRoutes.CUSTOM_PRODUCT),
          ),
          _buildServiceCard(
            icon: Icons.api,
            title: '第三方服务',
            onTap: () => Get.toNamed(AppRoutes.API_SERVICE),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        child: CircleAvatar(
          backgroundImage: AssetImage('assets/images/avatars/ai_assistant.png'),
        ),
        onPressed: controller.onAIAssistantTap,
      ),
    );
  }

  Widget _buildServiceCard({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 48),
            SizedBox(height: 8),
            Text(title),
          ],
        ),
      ),
    );
  }
} 