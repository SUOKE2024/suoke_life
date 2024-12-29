import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/suoke/suoke_controller.dart';

class SuokePage extends GetView<SuokeController> {
  const SuokePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SUOKE'),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        
        return GridView.builder(
          padding: const EdgeInsets.all(16),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: 16,
            crossAxisSpacing: 16,
            childAspectRatio: 1.2,
          ),
          itemCount: controller.services.length,
          itemBuilder: (context, index) {
            final service = controller.services[index];
            return Card(
              child: InkWell(
                onTap: () => controller.openService(service),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(service.icon, size: 48),
                    const SizedBox(height: 8),
                    Text(service.name),
                  ],
                ),
              ),
            );
          },
        );
      }),
    );
  }
} 