import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/life/health_stats_bloc.dart';
import 'package:fl_chart/fl_chart.dart';

@RoutePage()
class HealthStatsPage extends StatelessWidget {
  const HealthStatsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<HealthStatsBloc>()
        ..add(const HealthStatsEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('健康统计'),
          actions: [
            IconButton(
              icon: const Icon(Icons.date_range),
              onPressed: () {
                // 显示日期范围选择器
              },
            ),
            IconButton(
              icon: const Icon(Icons.share),
              onPressed: () {
                // 分享统计数据
              },
            ),
          ],
        ),
        body: BlocBuilder<HealthStatsBloc, HealthStatsState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (stats) => ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _buildHealthScoreCard(stats.healthScore),
                  const SizedBox(height: 16),
                  _buildActivityChart(stats.activityData),
                  const SizedBox(height: 16),
                  _buildSleepQualityChart(stats.sleepData),
                  const SizedBox(height: 16),
                  _buildMoodChart(stats.moodData),
                ],
              ),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
      ),
    );
  }

  Widget _buildHealthScoreCard(int score) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              '健康评分',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              score.toString(),
              style: const TextStyle(
                fontSize: 48,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityChart(List<ActivityData> data) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '活动统计',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                // 实现活动数据图表
                LineChartData(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ... 其他图表实现
} 