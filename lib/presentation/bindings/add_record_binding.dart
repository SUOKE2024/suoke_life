import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/add_record_controller.dart';

class AddRecordBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => AddRecordController());
  }
} 