import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'health_detection_service.dart';

class ExerciseService extends GetxService {
  final StorageService _storageService = Get.find();
  final HealthDetectionService _healthService = Get.find();

  final isTracking = false.obs;
  final currentExercise = Rx<Map<String, dynamic>?>(null);
  final exerciseData = <String, dynamic>{}.obs;

  // 开始运动
  Future<void> startExercise(String type) async {
    if (isTracking.value) return;

    try {
      isTracking.value = true;
      currentExercise.value = {
        'id': DateTime.now().toString(),
        'type': type,
        'start_time': DateTime.now().toIso8601String(),
        'data': {},
      };
      _startTracking();
    } catch (e) {
      isTracking.value = false;
      rethrow;
    }
  }

  // 结束运动
  Future<void> stopExercise() async {
    if (!isTracking.value) return;

    try {
      await _stopTracking();
      isTracking.value = false;
      await _saveExerciseRecord();
    } catch (e) {
      rethrow;
    }
  }

  // 获取运动历史
  Future<List<Map<String, dynamic>>> getExerciseHistory() async {
    try {
      final data = await _storageService.getLocal('exercise_records');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }

  void _startTracking() {
    // TODO: 实现运动数据追踪
  }

  Future<void> _stopTracking() async {
    // TODO: 停止运动数据追踪
  }

  Future<void> _saveExerciseRecord() async {
    if (currentExercise.value == null) return;

    try {
      final record = {
        ...currentExercise.value!,
        'end_time': DateTime.now().toIso8601String(),
        'data': exerciseData,
      };

      // 分析运动数据
      final analysis = await _healthService.detectHealthStatus(record);
      record['analysis'] = analysis;

      // 保存记录
      final records = await getExerciseHistory();
      records.insert(0, record);
      await _storageService.saveLocal('exercise_records', records);

      // 清除当前运动
      currentExercise.value = null;
      exerciseData.clear();
    } catch (e) {
      rethrow;
    }
  }
} 