import 'package:flutter/material.dart';
import '../../../services/ai/core_algorithm_service.dart';
import '../../../services/health/realtime_health_manager.dart';
import '../../../models/health/health_data.dart';
import 'health_metric_card.dart';
import 'health_trend_chart.dart';
import 'voice_analysis_card.dart';

class HealthAnalysisDashboard extends StatefulWidget {
  final CoreAlgorithmService algorithmService;
  final RealtimeHealthManager healthManager;

  const HealthAnalysisDashboard({
    Key? key,
    required this.algorithmService,
    required this.healthManager,
  }) : super(key: key);

  @override
  State<HealthAnalysisDashboard> createState() => _HealthAnalysisDashboardState();
}

class _HealthAnalysisDashboardState extends State<HealthAnalysisDashboard> {
  Map<String, dynamic>? _analysisResults;
  HealthData? _healthData;
  String? _error;

  @override
  void initState() {
    super.initState();
    _startMonitoring();
  }

  void _startMonitoring() {
    // 订阅健康数据流
    widget.healthManager.healthDataStream.listen(
      (healthData) {
        setState(() {
          _healthData = healthData;
          _error = null;
        });
      },
      onError: (error) {
        setState(() {
          _error = error.toString();
        });
      },
    );

    // 订阅分析结果流
    widget.healthManager.analysisResultStream.listen(
      (results) {
        setState(() {
          _analysisResults = results;
          _error = null;
        });
      },
      onError: (error) {
        setState(() {
          _error = error.toString();
        });
      },
    );

    // 开始监控
    widget.healthManager.startMonitoring();
  }

  @override
  void dispose() {
    widget.healthManager.stopMonitoring();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text('分析出错: $_error'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _startMonitoring,
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (_healthData == null || _analysisResults == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final healthAnalysis = _analysisResults!;
    final voiceAnalysis = _healthData!.metrics['voiceAnalysis'];

    return RefreshIndicator(
      onRefresh: () async {
        await widget.healthManager.stopMonitoring();
        _startMonitoring();
      },
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '健康分析报告',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            Text(
              '最后更新: ${_healthData!.timestamp.toString()}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 24),
            
            // 生命体征卡片
            HealthMetricCard(
              title: '生命体征',
              metrics: _healthData!.vitalSigns,
            ),
            const SizedBox(height: 16),
            
            // 生活方式分析
            HealthMetricCard(
              title: '生活方式分析',
              metrics: _healthData!.lifestyle,
            ),
            const SizedBox(height: 16),
            
            // 健康风险评估
            HealthMetricCard(
              title: '���康风险评估',
              metrics: healthAnalysis['risks'] as Map<String, dynamic>,
              isRisk: true,
            ),
            const SizedBox(height: 16),
            
            // 语音分析结果
            if (voiceAnalysis != null) ...[
              VoiceAnalysisCard(
                voiceAnalysis: voiceAnalysis as Map<String, dynamic>,
              ),
              const SizedBox(height: 16),
            ],
            
            // AI诊断结果
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'AI辅助诊断',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    Text(healthAnalysis['aiDiagnosis']['diagnosis'].toString()),
                    const Divider(),
                    Text(
                      '健康建议',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    ...List.generate(
                      (healthAnalysis['aiDiagnosis']['advice'] as List).length,
                      (index) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          children: [
                            const Icon(Icons.check_circle, size: 16),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                healthAnalysis['aiDiagnosis']['advice'][index],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            
            // 健康趋势图表
            HealthTrendChart(
              title: '近期健康趋势',
              data: healthAnalysis['trends'] as Map<String, dynamic>,
            ),
          ],
        ),
      ),
    );
  }
} 