import 'package:get/get.dart';
import '../data/models/record.dart';
import '../data/repositories/record_repository.dart';

class RecordsController extends GetxController {
  final RecordRepository _repository;
  
  RecordsController(this._repository);

  final recentRecords = <Record>[].obs;
  final isLoading = false.obs;

  @override
  void onInit() {
    super.onInit();
    loadRecentRecords();
  }

  Future<void> loadRecentRecords() async {
    try {
      isLoading.value = true;
      final records = await _repository.getRecentRecords();
      recentRecords.value = records;
    } catch (e) {
      Get.snackbar('错误', '加载记录失败：$e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> deleteRecord(String id) async {
    try {
      await _repository.deleteRecord(id);
      recentRecords.removeWhere((record) => record.id == id);
      Get.snackbar('成功', '记录已删除');
    } catch (e) {
      Get.snackbar('错误', '删除记录失败：$e');
    }
  }
} 