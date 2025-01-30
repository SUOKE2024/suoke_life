import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'health_detection_service.dart';

class RealtimeDataService extends GetxService {
  final StorageService _storageService = Get.find();
  final HealthDetectionService _healthService = Get.find();
  
  final isCollecting = false.obs;
  final currentData = <String, dynamic>{}.obs;

  // 开始数据采集
  Future<void> startCollection() async {
    if (isCollecting.value) return;
    
    try {
      isCollecting.value = true;
      await _initSensors();
      _startDataStream();
    } catch (e) {
      isCollecting.value = false;
      rethrow;
    }
  }

  // 停止数据采集
  Future<void> stopCollection() async {
    if (!isCollecting.value) return;
    
    try {
      await _stopDataStream();
      isCollecting.value = false;
      await _saveCollectedData();
    } catch (e) {
      rethrow;
    }
  }

  // 初始化传感器
  Future<void> _initSensors() async {
    print('Initializing sensors...');
    // 示例：初始化心率传感器、步数传感器等
    // 实际实现中需要根据具体传感器进行初始化
  }

  // 开始数据流
  void _startDataStream() {
    print('Starting data stream...');
    // 示例：开始采集心率数据、步数数据等
    // 实际实现中需要根据具体传感器进行数据采集
  }

  // 停止数据流
  Future<void> _stopDataStream() async {
    print('Stopping data stream...');
    // 示例：停止采集心率数据、步数数据等
    // 实际实现中需要根据具体传感器停止数据采集
  }

  // 保存采集的数据
  Future<void> _saveCollectedData() async {
    try {
      final analysisResult = await _healthService.detectHealthStatus(currentData.value);
      
      await _storageService.saveLocal('realtime_data_${DateTime.now().toIso8601String()}', {
        'data': currentData.value,
        'analysis': analysisResult,
        'timestamp': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      rethrow;
    }
  }
} 