import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/suoke/service_detail_controller.dart';

class ServiceDetailPage extends GetView<ServiceDetailController> {
  const ServiceDetailPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(controller.service.title),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 服务图片
            if (controller.service.imageUrl != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  controller.service.imageUrl!,
                  height: 200,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),
            const SizedBox(height: 16),
            // 服务描述
            Text(
              controller.service.description,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 24),
            // 服务内容
            ...controller.serviceContent.map((item) => Card(
              margin: const EdgeInsets.only(bottom: 16),
              child: ListTile(
                title: Text(item['title']),
                subtitle: Text(item['description']),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () => controller.openServiceItem(item),
              ),
            )),
          ],
        );
      }),
      floatingActionButton: FloatingActionButton(
        onPressed: () => controller.showXiaoI(),
        child: const Icon(Icons.chat),
      ),
    );
  }
} 