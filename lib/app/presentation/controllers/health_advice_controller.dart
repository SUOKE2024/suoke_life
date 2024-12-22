import 'package:get/get.dart';
import '../../data/models/health_advice.dart';
import '../../services/health_advice_service.dart';
import '../../core/error/error_handler.dart';
import '../../core/error/error_types.dart';
import 'package:flutter/material.dart';

class HealthAdviceController extends GetxController {
  final HealthAdviceService _service;
  
  final advices = <HealthAdvice>[].obs;
  final isLoading = false.obs;
  final error = Rx<String?>(null);
  final selectedLevel = Rx<AdviceLevel?>(null);
  final searchText = ''.obs;
  final filteredAdvices = <HealthAdvice>[].obs;
  final _searchController = TextEditingController();

  HealthAdviceController({
    required HealthAdviceService service,
  }) : _service = service;

  @override
  void onInit() async {
    super.onInit();
    await _service.loadFavorites();
    await _service.loadHistory();
    loadAdvices();
  }

  Future<void> loadAdvices() async {
    try {
      error.value = null;
      isLoading.value = true;
      await _service.loadAdvices();
      advices.assignAll(_service.advices);
    } catch (e) {
      error.value = '加载健康建议失败';
      ErrorHandler.handleError(AppException(
        type: ErrorType.health,
        message: '加载健康建议失败',
      ));
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> refreshAdvices() async {
    try {
      await loadAdvices();
      Get.snackbar('提示', '刷新成功');
    } catch (e) {
      ErrorHandler.handleError(e);
    }
  }

  void onAdviceTap(HealthAdvice advice) {
    Get.toNamed('/health/advice/${advice.id}', arguments: advice);
  }

  List<HealthAdvice> getAdvicesByLevel(AdviceLevel level) {
    return _service.getAdvicesByLevel(level);
  }

  List<HealthAdvice> getAdvicesByType(AdviceType type) {
    return _service.getAdvicesByType(type);
  }

  List<HealthAdvice> getUrgentAdvices() {
    return _service.getUrgentAdvices();
  }

  List<HealthAdvice> getHighPriorityAdvices() {
    return _service.getHighPriorityAdvices();
  }

  void filterByLevel(AdviceLevel level) {
    if (selectedLevel.value == level) {
      selectedLevel.value = null;
      filteredAdvices.clear();
    } else {
      selectedLevel.value = level;
      filteredAdvices.assignAll(_service.getAdvicesByLevel(level));
    }
  }

  void search(String text) {
    searchText.value = text;
    if (text.isEmpty) {
      filteredAdvices.clear();
      return;
    }
    
    final searchLower = text.toLowerCase().trim();
    filteredAdvices.assignAll(advices.where((advice) =>
      advice.title.toLowerCase().contains(searchLower) ||
      advice.content.toLowerCase().contains(searchLower) ||
      advice.tags.any((tag) => tag.toLowerCase().contains(searchLower)) ||
      _getTypeText(advice.type).toLowerCase().contains(searchLower)
    ));
  }

  Future<void> exportAdvices() async {
    try {
      await _service.exportToFile();
      Get.snackbar('成功', '导出成功');
    } catch (e) {
      ErrorHandler.handleError(e);
    }
  }

  @override
  void onClose() {
    _searchController.dispose();
    super.onClose();
    advices.clear();
    filteredAdvices.clear();
    error.value = null;
    selectedLevel.value = null;
    searchText.value = '';
  }
} 