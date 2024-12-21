import 'package:get/get.dart';
import 'package:suoke_life/services/sync_service.dart';

class SyncBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<SyncService>(() => SyncService());
  }
} 