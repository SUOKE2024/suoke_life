import 'package:health/health.dart';
import 'package:permission_handler/permission_handler.dart';

class HealthService {
  final HealthFactory _health;
  bool _isInitialized = false;

  HealthService() : _health = HealthFactory();

  Future<void> init() async {
    final status = await Permission.activityRecognition.request();
    if (status != PermissionStatus.granted) {
      throw Exception('需要健康数据权限');
    }

    final types = [
      HealthDataType.STEPS,
      HealthDataType.HEART_RATE,
      HealthDataType.BLOOD_PRESSURE_SYSTOLIC,
      HealthDataType.BLOOD_PRESSURE_DIASTOLIC,
      HealthDataType.BLOOD_OXYGEN,
      HealthDataType.BODY_TEMPERATURE,
      HealthDataType.SLEEP_ASLEEP,
    ];

    _isInitialized = await _health.requestAuthorization(types);
  }

  Future<Map<HealthDataType, double>> getHealthData(
    DateTime startTime,
    DateTime endTime,
  ) async {
    if (!_isInitialized) {
      throw Exception('健康服务未初始化');
    }

    final results = <HealthDataType, double>{};

    try {
      // 获取步数
      final steps = await _health.getTotalStepsInInterval(startTime, endTime);
      if (steps != null) {
        results[HealthDataType.STEPS] = steps.toDouble();
      }

      // 获取心率
      final heartRateData = await _health.getHealthDataFromTypes(
        startTime,
        endTime,
        [HealthDataType.HEART_RATE],
      );
      if (heartRateData.isNotEmpty) {
        results[HealthDataType.HEART_RATE] = 
            heartRateData.last.value.toDouble();
      }

      // 获取血压
      final bpData = await _health.getHealthDataFromTypes(
        startTime,
        endTime,
        [
          HealthDataType.BLOOD_PRESSURE_SYSTOLIC,
          HealthDataType.BLOOD_PRESSURE_DIASTOLIC,
        ],
      );
      if (bpData.isNotEmpty) {
        for (var data in bpData) {
          results[data.type] = data.value.toDouble();
        }
      }

      // 获取血氧
      final spo2Data = await _health.getHealthDataFromTypes(
        startTime,
        endTime,
        [HealthDataType.BLOOD_OXYGEN],
      );
      if (spo2Data.isNotEmpty) {
        results[HealthDataType.BLOOD_OXYGEN] = 
            spo2Data.last.value.toDouble();
      }

    } catch (e) {
      print('Error getting health data: $e');
      throw Exception('获取健康数据失败');
    }

    return results;
  }

  Future<Duration> getSleepDuration(
    DateTime date,
  ) async {
    if (!_isInitialized) {
      throw Exception('健康服务未初始化');
    }

    try {
      final startTime = DateTime(date.year, date.month, date.day);
      final endTime = startTime.add(const Duration(days: 1));

      final sleepData = await _health.getHealthDataFromTypes(
        startTime,
        endTime,
        [HealthDataType.SLEEP_ASLEEP],
      );

      int totalMinutes = 0;
      for (var data in sleepData) {
        totalMinutes += data.value.round();
      }

      return Duration(minutes: totalMinutes);
    } catch (e) {
      print('Error getting sleep data: $e');
      throw Exception('获取睡眠数据失败');
    }
  }
} 