import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/life/health_advice_detail_controller.dart';

class HealthAdviceDetailPage extends GetView<HealthAdviceDetailController> {
  const HealthAdviceDetailPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('健康建议'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: controller.shareAdvice,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Obx(() => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              controller.advice.value.title,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              controller.advice.value.content,
              style: const TextStyle(
                fontSize: 16,
                height: 1.6,
              ),
            ),
            if (controller.advice.value.recommendations.isNotEmpty) ...[
              const SizedBox(height: 32),
              const Text(
                '相关建议',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: controller.advice.value.recommendations.length,
                itemBuilder: (context, index) {
                  final recommendation = controller.advice.value.recommendations[index];
                  return ListTile(
                    leading: const Icon(Icons.lightbulb_outline),
                    title: Text(recommendation),
                  );
                },
              ),
            ],
          ],
        )),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton(
            onPressed: controller.startAction,
            child: const Text('开始行动'),
          ),
        ),
      ),
    );
  }
} 