import 'package:get/get.dart';
import '../presentation/controllers/main_controller.dart';
import '../services/auth_service.dart';

class MainBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<MainController>(() => MainController());
  }
} 