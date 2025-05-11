import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/models/health_record_model.dart';
import 'package:suoke_life/domain/models/sleep_analysis_model.dart';
import 'package:suoke_life/presentation/life/add_health_record_screen.dart';
import 'package:suoke_life/presentation/life/health_record_detail_screen.dart';
import 'package:suoke_life/presentation/life/health_records_list_screen.dart';
import 'package:suoke_life/presentation/life/sleep_analysis/sleep_analysis_screen.dart';
import 'package:suoke_life/presentation/life/sleep_analysis/sleep_trend_screen.dart';
import 'package:suoke_life/presentation/life/view_models/health_record_view_model.dart';
import 'package:auto_route/auto_route.dart';

/// LIFE模块主页面
@RoutePage()
class LifeScreen extends ConsumerStatefulWidget {
  const LifeScreen({super.key});

  @override
  ConsumerState<LifeScreen> createState() => _LifeScreenState();
}

class _LifeScreenState extends ConsumerState<LifeScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();

    // 创建标签控制器
    _tabController = TabController(length: 2, vsync: this);

    // 加载健康数据概览
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // 加载最近健康记录
      ref.read(healthRecordViewModelProvider.notifier).getRecentRecords(5);
      // 加载最近睡眠分析
      ref.read(sleepAnalysisViewModelProvider.notifier).getRecentAnalyses(5);
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('LIFE'),
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '概览'),
            Tab(text: '健康分析'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildOverviewTab(),
          _buildAnalysisTab(),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showQuickAddOptions,
        child: const Icon(Icons.add),
        tooltip: '快速记录',
      ),
    );
  }

  /// 构建概览标签页
  Widget _buildOverviewTab() {
    final healthState = ref.watch(healthRecordViewModelProvider);
    final sleepAnalysisState = ref.watch(sleepAnalysisViewModelProvider);

    return RefreshIndicator(
      onRefresh: () async {
        await ref
            .read(healthRecordViewModelProvider.notifier)
            .getRecentRecords(5);
        await ref
            .read(sleepAnalysisViewModelProvider.notifier)
            .getRecentAnalyses(5);
      },
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // 健康数据概览卡片
          Card(
            elevation: 2.0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16.0),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        '健康数据概览',
                        style: TextStyle(
                          fontSize: 18.0,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) =>
                                const HealthRecordsListScreen(),
                          ),
                        ),
                        child: const Text('查看全部'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16.0),

                  // 健康数据统计
                  _buildHealthStatsGrid(),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16.0),

          // 最近记录卡片
          Card(
            elevation: 2.0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16.0),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        '最近记录',
                        style: TextStyle(
                          fontSize: 18.0,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) =>
                                const HealthRecordsListScreen(),
                          ),
                        ),
                        child: const Text('查看全部'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8.0),

                  // 最近记录列表
                  healthState.isLoading
                      ? const Center(child: CircularProgressIndicator())
                      : healthState.records.isEmpty
                          ? const Center(
                              child: Text('暂无健康记录',
                                  style: TextStyle(color: Colors.grey)),
                            )
                          : Column(
                              children:
                                  healthState.records.take(5).map((record) {
                                return _buildRecentRecordItem(record);
                              }).toList(),
                            ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16.0),

          // 睡眠分析卡片
          Card(
            elevation: 2.0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16.0),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        '睡眠分析',
                        style: TextStyle(
                          fontSize: 18.0,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) => const SleepTrendScreen(),
                          ),
                        ),
                        child: const Text('查看趋势'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16.0),

                  // 最近睡眠分析
                  sleepAnalysisState.isLoading
                      ? const Center(child: CircularProgressIndicator())
                      : sleepAnalysisState.analyses.isEmpty
                          ? const Center(
                              child: Text('暂无睡眠分析数据',
                                  style: TextStyle(color: Colors.grey)),
                            )
                          : _buildRecentSleepAnalysis(
                              sleepAnalysisState.analyses.first),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建健康统计网格
  Widget _buildHealthStatsGrid() {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12.0,
      crossAxisSpacing: 12.0,
      childAspectRatio: 2.0,
      children: [
        _buildHealthStatTile(
          icon: Icons.nightlight_round,
          iconColor: Colors.indigo,
          title: '平均睡眠',
          value: '7.2小时',
        ),
        _buildHealthStatTile(
          icon: Icons.favorite,
          iconColor: Colors.red,
          title: '最近血压',
          value: '120/80',
        ),
        _buildHealthStatTile(
          icon: Icons.monitor_weight,
          iconColor: Colors.green,
          title: '体重趋势',
          value: '66.5kg',
        ),
        _buildHealthStatTile(
          icon: Icons.favorite_border,
          iconColor: Colors.orange,
          title: '平均心率',
          value: '72bpm',
        ),
      ],
    );
  }

  /// 构建健康统计瓦片
  Widget _buildHealthStatTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String value,
  }) {
    return Container(
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: iconColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12.0),
      ),
      child: Row(
        children: [
          Icon(icon, color: iconColor, size: 28.0),
          const SizedBox(width: 12.0),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14.0,
                    color: Colors.grey,
                  ),
                ),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 16.0,
                    fontWeight: FontWeight.bold,
                    color: iconColor,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 构建最近记录项
  Widget _buildRecentRecordItem(HealthRecord record) {
    final dateFormatter = DateFormat('MM月dd日 HH:mm');
    final dateString = dateFormatter.format(record.recordTime);

    IconData icon;
    Color color;
    String title;
    String value;

    switch (record.type) {
      case HealthDataType.sleep:
        final sleepRecord = record as SleepRecord;
        icon = Icons.nightlight_round;
        color = Colors.indigo;
        title = '睡眠记录';
        value = '${sleepRecord.durationHours.toStringAsFixed(1)}小时';
        break;
      case HealthDataType.bloodPressure:
        final bpRecord = record as BloodPressureRecord;
        icon = Icons.favorite;
        color = Colors.red;
        title = '血压记录';
        value = '${bpRecord.systolic}/${bpRecord.diastolic}';
        break;
      case HealthDataType.weight:
        final weightRecord = record as WeightRecord;
        icon = Icons.monitor_weight;
        color = Colors.green;
        title = '体重记录';
        value = '${weightRecord.weight.toStringAsFixed(1)}kg';
        break;
      case HealthDataType.heartRate:
        final hrRecord = record as HeartRateRecord;
        icon = Icons.favorite_border;
        color = Colors.orange;
        title = '心率记录';
        value = '${hrRecord.beatsPerMinute}bpm';
        break;
      default:
        icon = Icons.healing;
        color = Colors.grey;
        title = '健康记录';
        value = '';
        break;
    }

    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: CircleAvatar(
        backgroundColor: color.withOpacity(0.2),
        child: Icon(icon, color: color, size: 20.0),
      ),
      title: Text(title),
      subtitle: Text(dateString),
      trailing: Text(
        value,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.bold,
        ),
      ),
      onTap: () => Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => HealthRecordDetailScreen(recordId: record.id),
        ),
      ),
    );
  }

  /// 构建最近睡眠分析
  Widget _buildRecentSleepAnalysis(SleepAnalysis analysis) {
    final dateFormatter = DateFormat('MM月dd日');
    final dateString = dateFormatter.format(analysis.date);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$dateString 睡眠得分: ${analysis.overallScore.round()}分',
          style: const TextStyle(
            fontSize: 16.0,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12.0),

        // 睡眠质量指标
        Row(
          children: [
            Expanded(
              child: _buildSleepQualityItem(
                icon: Icons.timelapse,
                label: '总时长',
                value: '${analysis.durationHours.toStringAsFixed(1)}小时',
                color: Colors.blue,
              ),
            ),
            Expanded(
              child: _buildSleepQualityItem(
                icon: Icons.bedtime,
                label: '深睡时长',
                value: '${analysis.deepSleepHours.toStringAsFixed(1)}小时',
                color: Colors.indigo,
              ),
            ),
            Expanded(
              child: _buildSleepQualityItem(
                icon: Icons.nightlight,
                label: '入睡时间',
                value: '${DateFormat('HH:mm').format(analysis.bedtime)}',
                color: Colors.purple,
              ),
            ),
          ],
        ),

        const SizedBox(height: 16.0),

        // 查看详情按钮
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(
                builder: (context) =>
                    SleepAnalysisScreen(sleepRecordId: analysis.id),
              ),
            ),
            style: ElevatedButton.styleFrom(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.0),
              ),
            ),
            child: const Text('查看详细分析'),
          ),
        ),
      ],
    );
  }

  /// 构建睡眠质量项
  Widget _buildSleepQualityItem({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24.0),
        const SizedBox(height: 4.0),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12.0,
            color: Colors.grey,
          ),
        ),
        const SizedBox(height: 2.0),
        Text(
          value,
          style: TextStyle(
            fontSize: 14.0,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  /// 构建分析标签页
  Widget _buildAnalysisTab() {
    return ListView(
      padding: const EdgeInsets.all(16.0),
      children: [
        // 睡眠分析卡片
        Card(
          elevation: 2.0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.0),
          ),
          child: InkWell(
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(
                builder: (context) => const SleepTrendScreen(),
              ),
            ),
            borderRadius: BorderRadius.circular(16.0),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.nightlight_round,
                        color: Colors.indigo,
                        size: 28.0,
                      ),
                      const SizedBox(width: 12.0),
                      const Expanded(
                        child: Text(
                          '睡眠分析',
                          style: TextStyle(
                            fontSize: 18.0,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Icon(Icons.arrow_forward_ios, size: 16.0),
                    ],
                  ),
                  const SizedBox(height: 16.0),
                  const Text(
                    '分析您的睡眠质量和模式，提供改善建议',
                    style: TextStyle(
                      fontSize: 14.0,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 8.0),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      _buildAnalysisFeature(
                        label: '睡眠周期分析',
                      ),
                      const SizedBox(width: 8.0),
                      _buildAnalysisFeature(
                        label: '睡眠得分趋势',
                      ),
                      const SizedBox(width: 8.0),
                      _buildAnalysisFeature(
                        label: '智能改善建议',
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),

        const SizedBox(height: 16.0),

        // 血压分析卡片
        Card(
          elevation: 2.0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.0),
          ),
          child: InkWell(
            onTap: () {
              // TODO: 实现血压分析趋势页面
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('血压分析功能即将上线')),
              );
            },
            borderRadius: BorderRadius.circular(16.0),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.favorite,
                        color: Colors.red,
                        size: 28.0,
                      ),
                      const SizedBox(width: 12.0),
                      const Expanded(
                        child: Text(
                          '血压分析',
                          style: TextStyle(
                            fontSize: 18.0,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Icon(Icons.arrow_forward_ios, size: 16.0),
                    ],
                  ),
                  const SizedBox(height: 16.0),
                  const Text(
                    '追踪血压变化趋势，评估心血管健康风险',
                    style: TextStyle(
                      fontSize: 14.0,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 8.0),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      _buildAnalysisFeature(
                        label: '血压趋势图',
                      ),
                      const SizedBox(width: 8.0),
                      _buildAnalysisFeature(
                        label: '风险评估',
                      ),
                      const SizedBox(width: 8.0),
                      _buildAnalysisFeature(
                        label: '中医体质关联',
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),

        const SizedBox(height: 16.0),

        // 体重分析卡片
        Card(
          elevation: 2.0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.0),
          ),
          child: InkWell(
            onTap: () {
              // TODO: 实现体重分析趋势页面
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('体重分析功能即将上线')),
              );
            },
            borderRadius: BorderRadius.circular(16.0),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.monitor_weight,
                        color: Colors.green,
                        size: 28.0,
                      ),
                      const SizedBox(width: 12.0),
                      const Expanded(
                        child: Text(
                          '体重分析',
                          style: TextStyle(
                            fontSize: 18.0,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Icon(Icons.arrow_forward_ios, size: 16.0),
                    ],
                  ),
                  const SizedBox(height: 16.0),
                  const Text(
                    '监测体重变化，分析身体组成趋势',
                    style: TextStyle(
                      fontSize: 14.0,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 8.0),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      _buildAnalysisFeature(
                        label: '体重变化曲线',
                      ),
                      const SizedBox(width: 8.0),
                      _buildAnalysisFeature(
                        label: 'BMI趋势',
                      ),
                      const SizedBox(width: 8.0),
                      _buildAnalysisFeature(
                        label: '体脂率分析',
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),

        const SizedBox(height: 16.0),

        // 心率分析卡片
        Card(
          elevation: 2.0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.0),
          ),
          child: InkWell(
            onTap: () {
              // TODO: 实现心率分析趋势页面
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('心率分析功能即将上线')),
              );
            },
            borderRadius: BorderRadius.circular(16.0),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.favorite_border,
                        color: Colors.orange,
                        size: 28.0,
                      ),
                      const SizedBox(width: 12.0),
                      const Expanded(
                        child: Text(
                          '心率分析',
                          style: TextStyle(
                            fontSize: 18.0,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Icon(Icons.arrow_forward_ios, size: 16.0),
                    ],
                  ),
                  const SizedBox(height: 16.0),
                  const Text(
                    '分析不同状态下的心率表现，评估心脏健康',
                    style: TextStyle(
                      fontSize: 14.0,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 8.0),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      _buildAnalysisFeature(
                        label: '静息心率趋势',
                      ),
                      const SizedBox(width: 8.0),
                      _buildAnalysisFeature(
                        label: '心率区间分析',
                      ),
                      const SizedBox(width: 8.0),
                      _buildAnalysisFeature(
                        label: '心率变异性',
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  /// 构建分析特性标签
  Widget _buildAnalysisFeature({
    required String label,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
      decoration: BoxDecoration(
        color: Colors.grey.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12.0),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12.0,
          color: Colors.grey.shade700,
        ),
      ),
    );
  }

  /// 显示快速添加选项
  void _showQuickAddOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16.0)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                '快速记录',
                style: TextStyle(
                  fontSize: 18.0,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16.0),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildQuickAddButton(
                    icon: Icons.nightlight_round,
                    iconColor: Colors.indigo,
                    label: '睡眠',
                    onTap: () {
                      Navigator.of(context).pop();
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => AddHealthRecordScreen(
                            initialType: HealthDataType.sleep,
                          ),
                        ),
                      );
                    },
                  ),
                  _buildQuickAddButton(
                    icon: Icons.favorite,
                    iconColor: Colors.red,
                    label: '血压',
                    onTap: () {
                      Navigator.of(context).pop();
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => AddHealthRecordScreen(
                            initialType: HealthDataType.bloodPressure,
                          ),
                        ),
                      );
                    },
                  ),
                ],
              ),
              const SizedBox(height: 16.0),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildQuickAddButton(
                    icon: Icons.monitor_weight,
                    iconColor: Colors.green,
                    label: '体重',
                    onTap: () {
                      Navigator.of(context).pop();
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => AddHealthRecordScreen(
                            initialType: HealthDataType.weight,
                          ),
                        ),
                      );
                    },
                  ),
                  _buildQuickAddButton(
                    icon: Icons.favorite_border,
                    iconColor: Colors.orange,
                    label: '心率',
                    onTap: () {
                      Navigator.of(context).pop();
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => AddHealthRecordScreen(
                            initialType: HealthDataType.heartRate,
                          ),
                        ),
                      );
                    },
                  ),
                ],
              ),
              const SizedBox(height: 16.0),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('取消'),
              ),
            ],
          ),
        );
      },
    );
  }

  /// 构建快速添加按钮
  Widget _buildQuickAddButton({
    required IconData icon,
    required Color iconColor,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12.0),
      child: Container(
        width: 100.0,
        padding: const EdgeInsets.all(16.0),
        decoration: BoxDecoration(
          color: iconColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12.0),
        ),
        child: Column(
          children: [
            Icon(icon, color: iconColor, size: 32.0),
            const SizedBox(height: 8.0),
            Text(
              label,
              style: TextStyle(
                color: iconColor,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
