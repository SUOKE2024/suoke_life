import 'package:get/get.dart';
import '../controllers/sync_conflict_controller.dart';
import '../../data/services/sync_service.dart';

class SyncConflictBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => SyncService());
    Get.lazyPut(() => SyncConflictController());
  }
} 