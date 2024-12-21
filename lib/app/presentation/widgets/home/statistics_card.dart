import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../controllers/statistics_controller.dart';

class StatisticsCard extends GetView<StatisticsController> {
  const StatisticsCard({Key? key}) : super(key: key);

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
                  '数据统计',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => Get.toNamed('/statistics'),
                  child: const Text('查看更多'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem(
                  label: '今日记录',
                  value: controller.todayRecords.toString(),
                ),
                _buildStatItem(
                  label: '本周记录',
                  value: controller.weekRecords.toString(),
                ),
                _buildStatItem(
                  label: '本月记录',
                  value: controller.monthRecords.toString(),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem({
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }
} 