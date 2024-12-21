import 'package:get/get.dart';
import 'package:suoke_life/services/life_record_service.dart';
import 'package:suoke_life/data/models/life_record.dart';
import 'package:suoke_life/routes/app_routes.dart';

class LifeController extends GetxController {
  final LifeRecordService _recordService = Get.find();
  
  // 生活记录列表
  final records = <LifeRecord>[].obs;
  
  // 加载状态
  final isLoading = false.obs;
  
  // 刷新状态
  final isRefreshing = false.obs;
  
  @override
  void onInit() {
    super.onInit();
    loadRecords();
  }

  // 加载记录
  Future<void> loadRecords() async {
    if (isLoading.value) return;
    
    try {
      isLoading.value = true;
      final data = await _recordService.getRecords();
      records.value = data;
    } catch (e) {
      Get.snackbar('错误', '加载记录失败: $e');
    } finally {
      isLoading.value = false;
    }
  }

  // 刷新记录
  Future<void> refreshRecords() async {
    if (isRefreshing.value) return;
    
    try {
      isRefreshing.value = true;
      await loadRecords();
    } finally {
      isRefreshing.value = false;
    }
  }

  // 添加记录
  void addRecord() {
    Get.toNamed(AppRoutes.ADD_RECORD);
  }

  // 查看记录详情
  void showRecordDetail(String id) {
    Get.toNamed(
      AppRoutes.RECORD_DETAIL,
      arguments: {'id': id},
    );
  }

  // 查看用户资料
  void showUserProfile(String userId) {
    Get.toNamed(
      AppRoutes.USER_PROFILE,
      arguments: {'userId': userId},
    );
  }

  // 管理标签
  void manageTag() {
    Get.toNamed(AppRoutes.TAG_MANAGER);
  }

  // 查看统计
  void showAnalytics() {
    Get.toNamed(AppRoutes.ANALYTICS);
  }

  // 导出数据
  void exportData() {
    Get.toNamed(AppRoutes.EXPORT);
  }

  // 搜索历史
  void searchHistory() {
    Get.toNamed(AppRoutes.SEARCH_HISTORY);
  }

  // 删除记录
  Future<void> deleteRecord(String id) async {
    try {
      await _recordService.deleteRecord(id);
      records.removeWhere((record) => record.id == id);
      Get.snackbar('成功', '记录已删除');
    } catch (e) {
      Get.snackbar('错误', '删除记录失败: $e');
    }
  }
} 