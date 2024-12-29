import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/life/life_controller.dart';

class LifePage extends GetView<LifeController> {
  const LifePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('LIFE'),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 用户画像
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('用户画像', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    Text(controller.userProfile.value),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            // 健康建议
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('健康建议', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    ...controller.healthAdvice.map((advice) => ListTile(
                      title: Text(advice),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () => controller.showAdviceDetail(advice),
                    )),
                  ],
                ),
              ),
            ),
          ],
        );
      }),
    );
  }
} 