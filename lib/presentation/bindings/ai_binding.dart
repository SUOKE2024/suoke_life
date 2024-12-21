import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/ai_controller.dart';

class AIBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<AIController>(() => AIController());
  }
} 