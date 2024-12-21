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
    // TODO: 初始化各种传感器
  }

  // 开始数据流
  void _startDataStream() {
    // TODO: 实现数据流采集
  }

  // 停止数据流
  Future<void> _stopDataStream() async {
    // TODO: 停止数据流
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