import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:suoke_life/lib/core/services/health_profile_service.dart';
import 'package:suoke_life/lib/core/models/health_profile.dart';
import 'package:provider/provider.dart';
import 'package:suoke_life/ui/common/common_scaffold.dart';

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

  @override
  Widget build(BuildContext context) {
    return CommonScaffold(
      title: 'Health Data Input',
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _heartRateController,
              decoration: InputDecoration(labelText: 'Heart Rate'),
            ),
            TextField(
              controller: _bloodPressureController,
              decoration: InputDecoration(labelText: 'Blood Pressure'),
            ),
            TextField(
              controller: _sleepDurationController,
              decoration: InputDecoration(labelText: 'Sleep Duration'),
            ),
            ElevatedButton(
              onPressed: _saveHealthData,
              child: Text('Save'),
            ),
          ],
        ),
      ),
    );
  }

  void _saveHealthData() {
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
}
