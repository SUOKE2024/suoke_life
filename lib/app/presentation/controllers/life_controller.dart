import 'package:get/get.dart';
import '../../data/models/life_record.dart';
import '../../services/life_service.dart';

class LifeController extends GetxController {
  final LifeService _lifeService = Get.find();
  final records = <LifeRecord>[].obs;

  @override
  void onInit() {
    super.onInit();
    loadRecords();
  }

  Future<void> loadRecords() async {
    try {
      final items = await _lifeService.getLifeRecords();
      records.value = items;
    } catch (e) {
      Get.snackbar('错误', '加载记录失败');
    }
  }

  Future<void> addRecord(LifeRecord record) async {
    try {
      await _lifeService.addLifeRecord(record);
      records.insert(0, record);
    } catch (e) {
      Get.snackbar('错误', '添加记录失败');
    }
  }

  Future<void> deleteRecord(String id) async {
    try {
      await _lifeService.deleteLifeRecord(id);
      records.removeWhere((record) => record.id == id);
    } catch (e) {
      Get.snackbar('错误', '删除记录失败');
    }
  }
} 