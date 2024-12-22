import 'package:get/get.dart';
import '../controllers/health_advice_detail_controller.dart';
import '../../services/health_advice_service.dart';

class HealthAdviceDetailBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => HealthAdviceService(provider: Get.find()));
    Get.lazyPut(() => HealthAdviceDetailController());
  }
} 