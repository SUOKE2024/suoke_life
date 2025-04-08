import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/services/context_aware_sensing_service.dart';
import 'package:suoke_life/core/services/sensor_health_connector.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/core/models/context_data.dart';

@RoutePage()
class HealthProfilePage extends ConsumerStatefulWidget {
  const HealthProfilePage({Key? key}) : super(key: key);

  @override
  ConsumerState<HealthProfilePage> createState() => _HealthProfilePageState();
}

class _HealthProfilePageState extends ConsumerState<HealthProfilePage> {
  // 健康概览卡片
  Widget _buildHealthOverviewCard(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.favorite, color: AppColors.brandPrimary),
                const SizedBox(width: 8),
                Text(
                  '健康概览',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildHealthIndicator(
                  context,
                  '体质评分',
                  '85',
                  Icons.accessibility_new,
                  Colors.green,
                ),
                _buildHealthIndicator(
                  context,
                  '睡眠质量',
                  '良好',
                  Icons.nightlight_round,
                  Colors.blue,
                ),
                _buildHealthIndicator(
                  context,
                  '活动评分',
                  '75',
                  Icons.directions_run,
                  Colors.orange,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // 健康指标卡片
  Widget _buildHealthMetricsCard(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.area_chart, color: AppColors.brandPrimary),
                const SizedBox(width: 8),
                Text(
                  '健康指标',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildMetricItem(
              context,
              '平均心率',
              '72 bpm',
              Icons.monitor_heart,
              _buildMockLineChart(context, Colors.red.shade300),
            ),
            const Divider(),
            _buildMetricItem(
              context,
              '平均步数',
              '8,432 步/天',
              Icons.directions_walk,
              _buildMockLineChart(context, Colors.blue.shade300),
            ),
            const Divider(),
            _buildMetricItem(
              context,
              '平均睡眠',
              '7.2 小时/天',
              Icons.nightlight_round,
              _buildMockLineChart(context, Colors.purple.shade300),
            ),
          ],
        ),
      ),
    );
  }

  // 健康建议卡片
  Widget _buildHealthRecommendationsCard(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.lightbulb, color: AppColors.brandPrimary),
                const SizedBox(width: 8),
                Text(
                  '健康建议',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Consumer(
              builder: (context, ref, child) {
                final healthConnector =
                    ref.watch(sensorHealthConnectorProvider);
                final advices =
                    healthConnector.getComprehensiveAdvices(limit: 3);

                return Column(
                  children: advices.map((advice) {
                    IconData icon;
                    switch (advice.type) {
                      case HealthAdviceType.activity:
                        icon = Icons.directions_run;
                        break;
                      case HealthAdviceType.environment:
                        icon = Icons.terrain;
                        break;
                      case HealthAdviceType.time:
                        icon = Icons.access_time;
                        break;
                      case HealthAdviceType.tcm:
                        icon = Icons.spa;
                        break;
                      case HealthAdviceType.general:
                      default:
                        icon = Icons.tips_and_updates;
                        break;
                    }

                    return _buildRecommendationItem(
                      context,
                      advice.content,
                      icon,
                    );
                  }).toList(),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  // 健康指标
  Widget _buildHealthIndicator(BuildContext context, String title, String value,
      IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 36),
        const SizedBox(height: 8),
        Text(
          value,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          title,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  // 指标项
  Widget _buildMetricItem(BuildContext context, String title, String value,
      IconData icon, Widget chart) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(icon, color: AppColors.brandPrimary),
          const SizedBox(width: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              Text(
                value,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ],
          ),
          const Spacer(),
          SizedBox(
            width: 100,
            height: 40,
            child: chart,
          ),
        ],
      ),
    );
  }

  // 建议项
  Widget _buildRecommendationItem(
      BuildContext context, String text, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: AppColors.brandSecondary, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(text),
          ),
        ],
      ),
    );
  }

  // 模拟线图
  Widget _buildMockLineChart(BuildContext context, Color color) {
    final random = Random();
    final points = List.generate(
      7,
      (i) => Offset(i.toDouble(), 10 + random.nextDouble() * 20),
    );

    return CustomPaint(
      painter: LineChartPainter(points: points, lineColor: color),
    );
  }

  // 传感器数据分析卡片
  Widget _buildSensorDataAnalysisCard(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.sensors, color: AppColors.brandPrimary),
                const SizedBox(width: 8),
                Text(
                  '传感器数据洞察',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Consumer(
              builder: (context, ref, child) {
                final contextService =
                    ref.watch(contextAwareSensingServiceProvider);
                final userContext = contextService.getCurrentContext();
                final isMonitoring = contextService.isMonitoring();

                if (!isMonitoring) {
                  return const Padding(
                    padding: EdgeInsets.symmetric(vertical: 8.0),
                    child: Text('未启用持续感知功能，无法提供洞察'),
                  );
                }

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildInsightItem(
                      context,
                      '当前活动',
                      userContext.activity.state.toString().split('.').last,
                      _getActivityIcon(userContext.activity.state),
                    ),
                    const SizedBox(height: 8),
                    _buildInsightItem(
                      context,
                      '环境类型',
                      userContext.environment.type.toString().split('.').last,
                      _getEnvironmentIcon(userContext.environment.type),
                    ),
                    const SizedBox(height: 8),
                    _buildInsightItem(
                      context,
                      '推断状态',
                      userContext.inferredState,
                      Icons.psychology,
                    ),
                    const SizedBox(height: 16),
                    _buildHealthRecommendation(context, userContext),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  // 健康推荐
  Widget _buildHealthRecommendation(
      BuildContext context, UserContext userContext) {
    final recommendations = _generateRecommendations(userContext);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '基于环境的健康建议',
          style: Theme.of(context).textTheme.titleSmall,
        ),
        const SizedBox(height: 8),
        ...recommendations.map((rec) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.tips_and_updates,
                      size: 16, color: AppColors.brandSecondary),
                  const SizedBox(width: 8),
                  Expanded(child: Text(rec)),
                ],
              ),
            )),
      ],
    );
  }

  // 洞察项
  Widget _buildInsightItem(
      BuildContext context, String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: AppColors.brandPrimary),
        const SizedBox(width: 8),
        Text(
          '$label:',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(width: 8),
        Text(value),
      ],
    );
  }

  // 获取活动图标
  IconData _getActivityIcon(ActivityState state) {
    switch (state) {
      case ActivityState.still:
        return Icons.accessibility;
      case ActivityState.walking:
        return Icons.directions_walk;
      case ActivityState.running:
        return Icons.directions_run;
      case ActivityState.onBicycle:
        return Icons.pedal_bike;
      case ActivityState.inVehicle:
        return Icons.directions_car;
      case ActivityState.onStairs:
        return Icons.stairs;
      case ActivityState.lyingDown:
        return Icons.hotel;
      case ActivityState.sitting:
        return Icons.chair;
      case ActivityState.standing:
        return Icons.accessibility_new;
      case ActivityState.tilting:
        return Icons.screen_rotation;
      case ActivityState.unknown:
      default:
        return Icons.help_outline;
    }
  }

  // 获取环境图标
  IconData _getEnvironmentIcon(EnvironmentType type) {
    switch (type) {
      case EnvironmentType.indoor:
        return Icons.home;
      case EnvironmentType.outdoor:
        return Icons.landscape;
      case EnvironmentType.moving:
        return Icons.moving;
      case EnvironmentType.workplace:
        return Icons.work;
      case EnvironmentType.home:
        return Icons.house;
      case EnvironmentType.social:
        return Icons.people;
      case EnvironmentType.publicTransport:
        return Icons.commute;
      case EnvironmentType.medical:
        return Icons.local_hospital;
      case EnvironmentType.nature:
        return Icons.forest;
      case EnvironmentType.noisy:
        return Icons.volume_up;
      case EnvironmentType.quiet:
        return Icons.volume_mute;
      case EnvironmentType.unknown:
      default:
        return Icons.help_outline;
    }
  }

  // 生成健康建议
  List<String> _generateRecommendations(UserContext userContext) {
    final recommendations = <String>[];
    final activity = userContext.activity.state;
    final environment = userContext.environment.type;

    // 基于活动的建议
    if (activity == ActivityState.sitting &&
        userContext.activity.duration > 3600) {
      recommendations.add('您已久坐超过1小时，建议站起来活动5-10分钟，缓解久坐带来的健康风险。');
    }

    if (activity == ActivityState.running ||
        activity == ActivityState.walking) {
      recommendations.add('检测到您正在进行有氧运动，请注意补充水分，保持均匀呼吸。');
    }

    // 基于环境的建议
    if (environment == EnvironmentType.noisy) {
      recommendations.add('您处于嘈杂环境中，长期噪音可能影响听力和睡眠质量，建议减少暴露时间或使用耳塞。');
    }

    if (environment == EnvironmentType.indoor &&
        userContext.environment.lightLevel < 100) {
      recommendations.add('室内光线较暗，长时间阅读或用眼可能导致视觉疲劳，建议增加照明或适当休息。');
    }

    // 生成随机建议，确保至少有3条
    final randomRecommendations = [
      '定期进行深呼吸练习，有助于减轻压力，提高注意力。',
      '每小时眺望远处20秒，可缓解视觉疲劳，保护眼睛健康。',
      '饮食中增加五彩蔬果，摄入多样化营养素，增强免疫力。',
      '保持规律作息，提高睡眠质量，促进身体恢复与再生。',
      '适当增加日常活动量，如步行、爬楼梯，改善心肺功能。',
    ];

    while (recommendations.length < 3) {
      final random = Random();
      final index = random.nextInt(randomRecommendations.length);
      final rec = randomRecommendations[index];
      if (!recommendations.contains(rec)) {
        recommendations.add(rec);
      }
    }

    return recommendations;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('健康画像'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 健康概览卡片
              _buildHealthOverviewCard(context),
              const SizedBox(height: 16),

              // 传感器数据分析卡片 - 新添加的部分
              _buildSensorDataAnalysisCard(context),
              const SizedBox(height: 16),

              // 其他健康指标卡片
              _buildHealthMetricsCard(context),
              const SizedBox(height: 16),

              // 健康建议卡片
              _buildHealthRecommendationsCard(context),
            ],
          ),
        ),
      ),
    );
  }
}

// 线图绘制器
class LineChartPainter extends CustomPainter {
  final List<Offset> points;
  final Color lineColor;

  LineChartPainter({required this.points, required this.lineColor});

  @override
  void paint(Canvas canvas, Size size) {
    // 定义画笔
    final paint = Paint()
      ..color = lineColor
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    // 创建路径
    final path = Path();

    // 设置缩放比例
    final double xScale = size.width / (points.length - 1);
    final double yScale = size.height / 30; // 假设数据范围在0-30之间

    // 移动到第一个点
    path.moveTo(0, size.height - points[0].dy * yScale);

    // 添加其他点
    for (int i = 1; i < points.length; i++) {
      path.lineTo(i * xScale, size.height - points[i].dy * yScale);
    }

    // 绘制路径
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
