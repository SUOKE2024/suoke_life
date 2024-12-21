import 'package:flutter/material.dart';
import '../../core/base/base_page.dart';
import '../../widgets/sync_stats_chart.dart';

class SyncLogPage extends BasePage {
  const SyncLogPage({Key? key}) : super(key: key);

  @override
  String get title => '同步日志';

  @override
  Widget buildBody(BuildContext context) {
    // 示例数据
    final stats = [
      SyncStats(date: DateTime.now().subtract(const Duration(days: 6)), count: 10),
      SyncStats(date: DateTime.now().subtract(const Duration(days: 5)), count: 15),
      SyncStats(date: DateTime.now().subtract(const Duration(days: 4)), count: 8),
      SyncStats(date: DateTime.now().subtract(const Duration(days: 3)), count: 12),
      SyncStats(date: DateTime.now().subtract(const Duration(days: 2)), count: 20),
      SyncStats(date: DateTime.now().subtract(const Duration(days: 1)), count: 16),
      SyncStats(date: DateTime.now(), count: 14),
    ];

    return Column(
      children: [
        SyncStatsChart(stats: stats),
        Expanded(
          child: ListView.builder(
            itemCount: stats.length,
            itemBuilder: (context, index) {
              final stat = stats[index];
              return ListTile(
                title: Text('${stat.date.year}-${stat.date.month}-${stat.date.day}'),
                trailing: Text('${stat.count} 条记录'),
              );
            },
          ),
        ),
      ],
    );
  }
} 