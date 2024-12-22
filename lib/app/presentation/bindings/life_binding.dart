import 'package:get/get.dart';
import '../controllers/life_controller.dart';
import '../../services/life_service.dart';

class LifeBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => LifeService());
    Get.lazyPut(() => LifeController());
  }
} 