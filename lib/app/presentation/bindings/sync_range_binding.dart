import 'package:get/get.dart';
import '../controllers/sync_range_controller.dart';
import '../../data/services/sync_service.dart';

class SyncRangeBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => SyncService());
    Get.lazyPut(() => SyncRangeController());
  }
} 