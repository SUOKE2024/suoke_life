import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/theme/app_theme.dart';
import '../../widgets/ai_assistant_card.dart';

class HomePage extends GetView<HomeController> {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('索克生活'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () => Get.toNamed('/notifications'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // AI助手卡片
            AiAssistantCard(
              title: '小艾',
              subtitle: '生活管家和健康服务',
              onTap: () => Get.toNamed('/ai/xiaoi'),
            ),
            AiAssistantCard(
              title: '老克',
              subtitle: '知识顾问',
              onTap: () => Get.toNamed('/ai/laoke'),
            ),
            AiAssistantCard(
              title: '小克',
              subtitle: '商务助手',
              onTap: () => Get.toNamed('/ai/xiaoke'),
            ),

            // 健康数据卡片
            Obx(() => HealthDataCard(
              data: controller.healthData.value,
              onTap: () => Get.toNamed('/health/details'),
            )),

            // 生活记录卡片
            Obx(() => LifeRecordCard(
              records: controller.lifeRecords,
              onTap: () => Get.toNamed('/life/records'),
            )),
          ],
        ),
      ),
      bottomNavigationBar: CustomBottomNavBar(
        currentIndex: 0,
        onTap: (index) => controller.changePage(index),
      ),
    );
  }
} 