import 'package:get/get.dart';
import '../../core/base/base_controller.dart';
import '../../data/services/sync_service.dart';

class SyncConflictController extends BaseController {
  final _syncService = Get.find<SyncService>();
  final selectedStrategy = '手动处理'.obs;

  Future<void> updateStrategy(String strategy) async {
    try {
      showLoading();
      // TODO: 保存冲突处理策略
      selectedStrategy.value = strategy;
      hideLoading();
      Get.back();
    } catch (e) {
      showError(e.toString());
    }
  }
} 