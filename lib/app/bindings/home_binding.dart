import 'package:get/get.dart';
import '../controllers/home_controller.dart';
import '../services/ai_service.dart';
import '../services/life_service.dart';

class HomeBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => AiService());
    Get.lazyPut(() => LifeService());
    Get.lazyPut(() => HomeController());
  }
} 