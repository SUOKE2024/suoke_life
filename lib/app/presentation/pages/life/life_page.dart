import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/life_controller.dart';
import '../../widgets/life_record_card.dart';

class LifePage extends GetView<LifeController> {
  const LifePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('生活记录'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => Get.toNamed('/life/record'),
          ),
        ],
      ),
      body: Obx(() => ListView.builder(
        itemCount: controller.records.length,
        itemBuilder: (context, index) {
          final record = controller.records[index];
          return LifeRecordCard(
            record: record,
            onTap: () => Get.toNamed('/life/detail/${record.id}'),
          );
        },
      )),
    );
  }
} 