import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/ai_controller.dart';
import 'package:suoke_life/routes/app_routes.dart';

class AIPage extends GetView<AIController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Obx(() => Text(controller.title)),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('AI助手'),
            ElevatedButton(
              onPressed: () => Get.toNamed(AppRoutes.AI_CHAT),
              child: Text('开始对话'),
            ),
          ],
        ),
      ),
    );
  }
} 