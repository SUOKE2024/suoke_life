import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/life_controller.dart';
import 'package:suoke_life/services/life_record_service.dart';

class LifeBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<LifeRecordService>(() => LifeRecordService());
    Get.lazyPut(() => LifeController());
  }
} 