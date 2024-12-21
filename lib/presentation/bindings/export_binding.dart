import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/export_controller.dart';

class ExportBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => ExportController());
  }
} 