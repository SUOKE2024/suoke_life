import 'package:get/get.dart';
import '../controllers/sync_log_controller.dart';
import '../../data/services/sync_service.dart';

class SyncLogBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => SyncService());
    Get.lazyPut(() => SyncLogController());
  }
} 