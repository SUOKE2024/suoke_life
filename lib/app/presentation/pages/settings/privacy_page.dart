import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/settings/privacy_controller.dart';

class PrivacyPage extends StatelessWidget {
  const PrivacyPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('隐私政策'),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '隐私政策',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                controller.privacyContent.value,
                style: const TextStyle(
                  fontSize: 16,
                  height: 1.6,
                ),
              ),
              const SizedBox(height: 32),
              const Text(
                '数据收集与使用',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: controller.dataUsage.length,
                itemBuilder: (context, index) {
                  final item = controller.dataUsage[index];
                  return ListTile(
                    title: Text(item.title),
                    subtitle: Text(item.description),
                  );
                },
              ),
            ],
          ),
        );
      }),
    );
  }
} 