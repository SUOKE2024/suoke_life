import 'package:get/get.dart';
import '../../core/base/base_controller.dart';
import '../../data/models/life_record.dart';
import '../../services/life_service.dart';

class LifeController extends BaseController {
  final LifeService _lifeService = Get.find();
  final records = <LifeRecord>[].obs;

  @override
  void onInit() {
    super.onInit();
    _loadRecords();
  }

  Future<void> _loadRecords() async {
    try {
      showLoading();
      final data = await _lifeService.getLifeRecords();
      records.value = data;
    } catch (e) {
      showError('加载生活记录失败');
    } finally {
      hideLoading();
    }
  }

  Future<void> addRecord(LifeRecord record) async {
    try {
      showLoading();
      await _lifeService.saveLifeRecord(record);
      await _loadRecords();
      Get.back();
      showSuccess('添加成功');
    } catch (e) {
      showError('添加失败');
    } finally {
      hideLoading();
    }
  }

  Future<void> updateRecord(LifeRecord record) async {
    try {
      showLoading();
      await _lifeService.updateLifeRecord(record);
      await _loadRecords();
      Get.back();
      showSuccess('更新成功');
    } catch (e) {
      showError('更新失败');
    } finally {
      hideLoading();
    }
  }

  Future<void> deleteRecord(String id) async {
    try {
      showLoading();
      await _lifeService.deleteLifeRecord(id);
      await _loadRecords();
      showSuccess('删除成功');
    } catch (e) {
      showError('删除失败');
    } finally {
      hideLoading();
    }
  }

  Future<void> searchRecords(String keyword) async {
    try {
      showLoading();
      final results = await _lifeService.searchLifeRecords(keyword);
      records.value = results;
    } catch (e) {
      showError('搜索失败');
    } finally {
      hideLoading();
    }
  }

  void clearSearch() {
    _loadRecords();
  }
} 