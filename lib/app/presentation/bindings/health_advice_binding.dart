import 'package:get/get.dart';
import '../controllers/health_advice_controller.dart';
import '../../services/health_advice_service.dart';
import '../../data/providers/health_advice_provider.dart';

class HealthAdviceBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => HealthAdviceProvider(Get.find()));
    Get.lazyPut(() => HealthAdviceService(provider: Get.find()));
    Get.lazyPut(() => HealthAdviceController(service: Get.find()));
  }
} 