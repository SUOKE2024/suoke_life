import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/models/sleep_analysis_model.dart';
import 'package:suoke_life/presentation/life/sleep_analysis/sleep_trend_screen.dart';

/// 睡眠分析屏幕
class SleepAnalysisScreen extends StatelessWidget {
  /// 睡眠记录ID
  final String sleepRecordId;

  /// 构造函数
  const SleepAnalysisScreen({
    Key? key,
    required this.sleepRecordId,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('睡眠分析'),
      ),
      body: Center(
        child: Text('睡眠记录ID: $sleepRecordId\n睡眠分析功能开发中'),
      ),
    );
  }
}

/// 睡眠分析详情页面
class SleepAnalysisScreenState extends ConsumerStatefulWidget {
  final String sleepRecordId;

  const SleepAnalysisScreenState({
    super.key,
    required this.sleepRecordId,
  });

  @override
  ConsumerState<SleepAnalysisScreenState> createState() =>
      _SleepAnalysisScreenState();
}

class _SleepAnalysisScreenState extends ConsumerState<SleepAnalysisScreenState>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final Duration _animationDuration = const Duration(milliseconds: 500);

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);

    // 在页面加载时分析睡眠记录
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref
          .read(sleepAnalysisViewModelProvider.notifier)
          .analyzeSleepRecord(widget.sleepRecordId);

      // 同时加载过去30天的睡眠趋势
      final now = DateTime.now();
      final thirtyDaysAgo = now.subtract(const Duration(days: 30));
      ref
          .read(sleepAnalysisViewModelProvider.notifier)
          .analyzeSleepTrend(thirtyDaysAgo, now);
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final analysisState = ref.watch(sleepAnalysisViewModelProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('睡眠分析'),
        centerTitle: true,
        actions: [
          // 添加查看睡眠趋势按钮
          IconButton(
            icon: const Icon(Icons.trending_up),
            tooltip: '查看睡眠趋势',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const SleepTrendScreen(),
                ),
              );
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '概览'),
            Tab(text: '睡眠周期'),
            Tab(text: '建议'),
          ],
        ),
      ),
      body: analysisState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : analysisState.errorMessage != null
              ? Center(child: Text('错误: ${analysisState.errorMessage}'))
              : analysisState.result == null
                  ? const Center(child: Text('无分析数据'))
                  : TabBarView(
                      controller: _tabController,
                      children: [
                        _buildOverviewTab(analysisState.result!),
                        _buildSleepCycleTab(analysisState.result!),
                        _buildSuggestionsTab(analysisState.suggestions),
                      ],
                    ),
    );
  }

  Widget _buildOverviewTab(SleepAnalysisResult analysis) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 睡眠质量评分卡片
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const Text(
                    '睡眠质量评分',
                    style: TextStyle(
                      fontSize: 18.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16.0),
                  TweenAnimationBuilder<double>(
                    duration: _animationDuration,
                    tween: Tween<double>(begin: 0, end: analysis.overallScore),
                    builder: (context, value, child) {
                      return Stack(
                        alignment: Alignment.center,
                        children: [
                          SizedBox(
                            height: 150,
                            width: 150,
                            child: CircularProgressIndicator(
                              value: value / 100,
                              strokeWidth: 12,
                              backgroundColor: Colors.grey[300],
                              valueColor: AlwaysStoppedAnimation<Color>(
                                _getScoreColor(value),
                              ),
                            ),
                          ),
                          Column(
                            children: [
                              Text(
                                value.toStringAsFixed(1),
                                style: const TextStyle(
                                  fontSize: 36,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                analysis.qualityLevel.label,
                                style: TextStyle(
                                  fontSize: 18,
                                  color: _getScoreColor(value),
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ],
                      );
                    },
                  ),
                  const SizedBox(height: 16.0),
                  // 睡眠时间信息
                  ListTile(
                    leading: const Icon(Icons.access_time),
                    title: const Text('睡眠时间'),
                    subtitle: Text(
                      '${analysis.sleepRecord.durationHours.toStringAsFixed(1)}小时',
                    ),
                    dense: true,
                  ),
                  ListTile(
                    leading: const Icon(Icons.speed),
                    title: const Text('睡眠效率'),
                    subtitle:
                        Text('${analysis.efficiency.toStringAsFixed(1)}%'),
                    dense: true,
                  ),
                  ListTile(
                    leading: const Icon(Icons.timelapse),
                    title: const Text('入睡时间'),
                    subtitle: Text('${analysis.timeToFallAsleepMinutes}分钟'),
                    dense: true,
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16.0),

          // 睡眠阶段比例卡片
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '睡眠阶段比例',
                    style: TextStyle(
                      fontSize: 18.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16.0),
                  Column(
                    children: [
                      _buildSleepPhaseProgressBar(
                        '深睡眠',
                        analysis.deepSleepPercentage,
                        Colors.indigo,
                      ),
                      const SizedBox(height: 8.0),
                      _buildSleepPhaseProgressBar(
                        '浅睡眠',
                        analysis.lightSleepPercentage,
                        Colors.blue,
                      ),
                      const SizedBox(height: 8.0),
                      _buildSleepPhaseProgressBar(
                        '快速眼动',
                        analysis.remSleepPercentage,
                        Colors.purple,
                      ),
                      const SizedBox(height: 8.0),
                      _buildSleepPhaseProgressBar(
                        '清醒',
                        analysis.awakePercentage,
                        Colors.orange,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16.0),

          // 中医体质评估卡片
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '中医体质评估',
                    style: TextStyle(
                      fontSize: 18.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16.0),
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8.0),
                    child: Text(
                      analysis.tcmEvaluation,
                      style: const TextStyle(fontSize: 16.0),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSleepPhaseProgressBar(
      String label, double percentage, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label),
              Text('${percentage.toStringAsFixed(1)}%'),
            ],
          ),
          const SizedBox(height: 4.0),
          TweenAnimationBuilder<double>(
            duration: _animationDuration,
            tween: Tween<double>(begin: 0, end: percentage / 100),
            builder: (context, value, child) {
              return LinearProgressIndicator(
                value: value,
                backgroundColor: Colors.grey[200],
                valueColor: AlwaysStoppedAnimation<Color>(color),
                minHeight: 8,
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSleepCycleTab(SleepAnalysisResult analysis) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '睡眠周期图',
                    style: TextStyle(
                      fontSize: 18.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16.0),
                  SizedBox(
                    height: 200,
                    child: _SleepCycleChart(
                      sleepStages: analysis.sleepStages,
                      animationDuration: _animationDuration,
                    ),
                  ),
                  const SizedBox(height: 16.0),
                  // 图例
                  Wrap(
                    spacing: 16.0,
                    children: [
                      _buildLegend('深睡眠', Colors.indigo),
                      _buildLegend('浅睡眠', Colors.blue),
                      _buildLegend('快速眼动', Colors.purple),
                      _buildLegend('清醒', Colors.orange),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16.0),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '睡眠阶段详情',
                    style: TextStyle(
                      fontSize: 18.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16.0),
                  ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: analysis.sleepStages.length,
                    itemBuilder: (context, index) {
                      final stage = analysis.sleepStages[index];
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: _getSleepStageColor(stage.type),
                          child: Text(
                            (index + 1).toString(),
                            style: const TextStyle(color: Colors.white),
                          ),
                        ),
                        title: Text(stage.type.label),
                        subtitle: Text(
                          '${_formatTime(stage.startTime)} - ${_formatTime(stage.endTime)}',
                        ),
                        trailing: Text('${stage.durationMinutes}分钟'),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLegend(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 16,
          height: 16,
          color: color,
        ),
        const SizedBox(width: 4),
        Text(label),
      ],
    );
  }

  Widget _buildSuggestionsTab(List<String> suggestions) {
    return ListView(
      padding: const EdgeInsets.all(16.0),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '改善建议',
                  style: TextStyle(
                    fontSize: 18.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16.0),
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: suggestions.length,
                  itemBuilder: (context, index) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(
                            Icons.lightbulb_outline,
                            color: Colors.amber,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              suggestions[index],
                              style: const TextStyle(fontSize: 16),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 90) return Colors.green;
    if (score >= 75) return Colors.lightGreen;
    if (score >= 60) return Colors.amber;
    if (score >= 40) return Colors.orange;
    return Colors.red;
  }

  Color _getSleepStageColor(SleepStageType type) {
    switch (type) {
      case SleepStageType.deep:
        return Colors.indigo;
      case SleepStageType.light:
        return Colors.blue;
      case SleepStageType.rem:
        return Colors.purple;
      case SleepStageType.awake:
        return Colors.orange;
    }
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}

/// 睡眠周期图表
class _SleepCycleChart extends StatelessWidget {
  final List<SleepStage> sleepStages;
  final Duration animationDuration;

  const _SleepCycleChart({
    required this.sleepStages,
    required this.animationDuration,
  });

  @override
  Widget build(BuildContext context) {
    // 按时间排序
    final sortedStages = List<SleepStage>.from(sleepStages)
      ..sort((a, b) => a.startTime.compareTo(b.startTime));

    // 如果没有阶段数据
    if (sortedStages.isEmpty) {
      return const Center(child: Text('无睡眠阶段数据'));
    }

    // 计算总时长（分钟）
    final totalMinutes = sortedStages.fold<int>(
      0,
      (sum, stage) => sum + stage.durationMinutes,
    );

    // 构建图表
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final height = constraints.maxHeight;

        return CustomPaint(
          size: Size(width, height),
          painter: _SleepCyclePainter(
            sleepStages: sortedStages,
            totalDuration: totalMinutes,
            animationDuration: animationDuration,
          ),
        );
      },
    );
  }
}

/// 睡眠周期图表绘制器
class _SleepCyclePainter extends CustomPainter {
  final List<SleepStage> sleepStages;
  final int totalDuration;
  final Duration animationDuration;

  _SleepCyclePainter({
    required this.sleepStages,
    required this.totalDuration,
    required this.animationDuration,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // 定义阶段高度位置
    final Map<SleepStageType, double> stageHeights = {
      SleepStageType.awake: size.height * 0.1,
      SleepStageType.rem: size.height * 0.4,
      SleepStageType.light: size.height * 0.7,
      SleepStageType.deep: size.height * 0.9,
    };

    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    // 绘制水平辅助线
    final linePaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0
      ..color = Colors.grey.withOpacity(0.3);

    stageHeights.forEach((stageType, height) {
      canvas.drawLine(
        Offset(0, height),
        Offset(size.width, height),
        linePaint,
      );
    });

    // 如果没有阶段，退出
    if (sleepStages.isEmpty) return;

    // 起始点
    final path = Path();
    var currentX = 0.0;
    var isFirstPoint = true;

    for (var i = 0; i < sleepStages.length; i++) {
      final stage = sleepStages[i];
      final stageWidth = (stage.durationMinutes / totalDuration) * size.width;
      final stageHeight = stageHeights[stage.type] ?? 0;

      // 如果是第一个点，移动到起点
      if (isFirstPoint) {
        path.moveTo(currentX, stageHeight);
        isFirstPoint = false;
      } else {
        // 否则连接到新点
        path.lineTo(currentX, stageHeight);
      }

      // 绘制阶段宽度
      currentX += stageWidth;
      path.lineTo(currentX, stageHeight);
    }

    // 为不同阶段设置不同颜色
    for (var i = 0; i < sleepStages.length; i++) {
      final stage = sleepStages[i];
      final stageWidth = (stage.durationMinutes / totalDuration) * size.width;
      final stageHeight = stageHeights[stage.type] ?? 0;
      final prevStageHeight =
          i > 0 ? stageHeights[sleepStages[i - 1].type] ?? 0 : stageHeight;

      final startX = i > 0
          ? sleepStages
                  .sublist(0, i)
                  .fold<int>(0, (sum, s) => sum + s.durationMinutes) /
              totalDuration *
              size.width
          : 0.0;

      final stagePath = Path();
      stagePath.moveTo(startX, prevStageHeight);
      stagePath.lineTo(startX, stageHeight);
      stagePath.lineTo(startX + stageWidth, stageHeight);

      if (i < sleepStages.length - 1) {
        final nextStageHeight = stageHeights[sleepStages[i + 1].type] ?? 0;
        stagePath.lineTo(startX + stageWidth, nextStageHeight);
      } else {
        stagePath.lineTo(startX + stageWidth, stageHeight);
      }

      // 设置阶段颜色
      switch (stage.type) {
        case SleepStageType.deep:
          paint.color = Colors.indigo;
          break;
        case SleepStageType.light:
          paint.color = Colors.blue;
          break;
        case SleepStageType.rem:
          paint.color = Colors.purple;
          break;
        case SleepStageType.awake:
          paint.color = Colors.orange;
          break;
      }

      canvas.drawPath(stagePath, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}
