import 'package:flutter/material.dart';
import '../../data/models/health_advice.dart';
import 'package:get/get.dart';
import '../../presentation/controllers/health_advice_controller.dart';

class HealthAdviceListHeader extends StatelessWidget {
  final List<HealthAdvice> advices;

  const HealthAdviceListHeader({
    Key? key,
    required this.advices,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final urgentCount = advices.where((a) => 
      a.level == AdviceLevel.urgent && !a.isExpired).length;
    final highCount = advices.where((a) => 
      a.level == AdviceLevel.high && !a.isExpired).length;
    final totalCount = advices.where((a) => !a.isExpired).length;

    return Card(
      margin: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '健康建议概览',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                IconButton(
                  icon: const Icon(Icons.file_download),
                  onPressed: () => Get.find<HealthAdviceController>().exportAdvices(),
                  tooltip: '导出健康建议',
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem(context, '紧急', urgentCount, Colors.red),
              _buildStatItem(context, '重要', highCount, Colors.orange),
              _buildStatItem(context, '总计', totalCount, Colors.blue),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(
    BuildContext context,
    String label,
    int count,
    Color color,
  ) {
    return Expanded(
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: label == '总计' ? null : () {
          if (label == '紧急') {
            Get.find<HealthAdviceController>().filterByLevel(AdviceLevel.urgent);
          } else if (label == '重要') {
            Get.find<HealthAdviceController>().filterByLevel(AdviceLevel.high);
          }
        },
        child: Column(
          children: [
            Text(
              count.toString(),
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: color,
              ),
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }
} 