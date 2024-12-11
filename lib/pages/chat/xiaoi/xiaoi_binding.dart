import 'package:get/get.dart';
import '../../../services/ai/ai_service.dart';
import 'xiaoi_controller.dart';

class XiaoiBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<AIService>(() => AIService());
    Get.lazyPut<XiaoiController>(() => XiaoiController(Get.find<AIService>()));
  }
} 