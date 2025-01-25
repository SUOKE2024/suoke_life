import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../controllers/records_controller.dart';
import '../../../data/models/record.dart';

class RecentRecords extends GetView<RecordsController> {
  const RecentRecords({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  '最近记录',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => Navigator.pushNamed('/records'),
                  child: const Text('查看全部'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Obx(() {
              if (controller.recentRecords.isEmpty) {
                return const Center(
                  child: Text('暂无记录'),
                );
              }
              return ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: controller.recentRecords.length,
                separatorBuilder: (context, index) => const Divider(),
                itemBuilder: (context, index) {
                  final record = controller.recentRecords[index];
                  return ListTile(
                    leading: Icon(
                      record.type.icon,
                      color: record.type.color,
                    ),
                    title: Text(record.title),
                    subtitle: Text(record.createdAt.format()),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.pushNamed(
                      '/record/detail',
                      arguments: record,
                    ),
                  );
                },
              );
            }),
          ],
        ),
      ),
    );
  }
} 