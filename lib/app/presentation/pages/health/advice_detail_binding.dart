import 'package:get/get.dart';
import '../../../services/health_advice_service.dart';
import '../../../data/providers/health_advice_provider.dart';
import '../../controllers/health_advice_detail_controller.dart';

class HealthAdviceDetailBinding extends Bindings {
  @override
  void dependencies() {
    // 确保 provider 和 service 已注入
    if (!Get.isRegistered<HealthAdviceProvider>()) {
      Get.lazyPut(() => HealthAdviceProvider(Get.find()));
    }
    if (!Get.isRegistered<HealthAdviceService>()) {
      Get.lazyPut(() => HealthAdviceService(provider: Get.find()));
    }
    
    // 注入详情控制器
    Get.lazyPut(() => HealthAdviceDetailController());
  }
} 