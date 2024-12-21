import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/suoke_controller.dart';
import '../../widgets/service_card.dart';
import '../../widgets/ai_assistant_bubble.dart';

class SuokePage extends GetView<SuokeController> {
  const SuokePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SUOKE服务'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: controller.showServiceMenu,
          ),
        ],
      ),
      body: Stack(
        children: [
          RefreshIndicator(
            onRefresh: controller.refreshServices,
            child: CustomScrollView(
              slivers: [
                // 健康服务区域
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '健康服务',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Obx(() => GridView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 2,
                            childAspectRatio: 1.5,
                            crossAxisSpacing: 16,
                            mainAxisSpacing: 16,
                          ),
                          itemCount: controller.healthServices.length,
                          itemBuilder: (context, index) {
                            final service = controller.healthServices[index];
                            return ServiceCard(
                              title: service.name,
                              description: service.description,
                              icon: service.icon,
                              onTap: () => controller.openService(service),
                            );
                          },
                        )),
                      ],
                    ),
                  ),
                ),

                // 农产品服务区域
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '农产品服务',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Obx(() => GridView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 2,
                            childAspectRatio: 1.5,
                            crossAxisSpacing: 16,
                            mainAxisSpacing: 16,
                          ),
                          itemCount: controller.agriServices.length,
                          itemBuilder: (context, index) {
                            final service = controller.agriServices[index];
                            return ServiceCard(
                              title: service.name,
                              description: service.description,
                              icon: service.icon,
                              onTap: () => controller.openService(service),
                            );
                          },
                        )),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          // AI助手小艾气泡
          Positioned(
            right: 16,
            bottom: 16,
            child: AIAssistantBubble(
              name: '小艾',
              onTap: () => controller.openAIChat('xiaoi'),
            ),
          ),
        ],
      ),
    );
  }
} 