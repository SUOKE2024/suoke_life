import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:suoke_life/core/services/health_profile_service.dart';
import 'package:suoke_life/core/models/health_profile.dart';

class HealthDataInputPage extends StatefulWidget {
  const HealthDataInputPage({super.key});

  @override
  State<HealthDataInputPage> createState() => _HealthDataInputPageState();
}

class _HealthDataInputPageState extends State<HealthDataInputPage> {
  final _heartRateController = TextEditingController();
  final _bloodPressureController = TextEditingController();
  final _sleepDurationController = TextEditingController();
  final HealthProfileService _healthProfileService =
      GetIt.I<HealthProfileService>();

  @override
  void dispose() {
    _heartRateController.dispose();
    _bloodPressureController.dispose();
    _sleepDurationController.dispose();
    super.dispose();
  }

  Future<void> _saveHealthData() async {
    const userId = 'defaultUserId'; //  TODO:  替换为实际用户 ID
    final healthMetrics = {
      'heartRate': _heartRateController.text,
      'bloodPressure': _bloodPressureController.text,
      'sleepDuration': _sleepDurationController.text,
    };

    final healthProfile =
        HealthProfile(userId: userId, healthMetrics: healthMetrics);

    try {
      await _healthProfileService.saveHealthProfile(healthProfile);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('健康数据已保存')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('保存健康数据失败: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('健康数据录入')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            TextField(
              controller: _heartRateController,
              decoration: const InputDecoration(labelText: '心率 (次/分钟)'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: _bloodPressureController,
              decoration:
                  const InputDecoration(labelText: '血压 (mmHg) 例如: 120/80'),
            ),
            TextField(
              controller: _sleepDurationController,
              decoration: const InputDecoration(labelText: '睡眠时长 (小时)'),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _saveHealthData,
              child: const Text('保存'),
            ),
          ],
        ),
      ),
    );
  }
}
