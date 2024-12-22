import 'package:get/get.dart';
import '../core/storage/storage_service.dart';

class HealthService extends GetxService {
  final StorageService _storageService = Get.find();
  
  final healthData = <String, dynamic>{}.obs;
  final healthMetrics = <String, List<Map<String, dynamic>>>{}.obs;
  final healthGoals = <String, Map<String, dynamic>>{}.obs;

  Future<HealthService> init() async {
    await _initHealth();
    return this;
  }

  Future<void> _initHealth() async {
    try {
      await Future.wait([
        _loadHealthData(),
        _loadHealthMetrics(),
        _loadHealthGoals(),
      ]);
    } catch (e) {
      print('Error initializing health: $e');
    }
  }

  Future<void> _loadHealthData() async {
    try {
      final data = await _storageService.getLocal('health_data');
      if (data != null) {
        healthData.value = Map<String, dynamic>.from(data);
      }
    } catch (e) {
      print('Error loading health data: $e');
    }
  }

  Future<void> _loadHealthMetrics() async {
    try {
      final metrics = await _storageService.getLocal('health_metrics');
      if (metrics != null) {
        healthMetrics.value = Map<String, List<Map<String, dynamic>>>.from(metrics);
      }
    } catch (e) {
      print('Error loading health metrics: $e');
    }
  }

  Future<void> _loadHealthGoals() async {
    try {
      final goals = await _storageService.getLocal('health_goals');
      if (goals != null) {
        healthGoals.value = Map<String, Map<String, dynamic>>.from(goals);
      }
    } catch (e) {
      print('Error loading health goals: $e');
    }
  }
} 