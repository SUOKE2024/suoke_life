import 'package:get/get.dart';
import '../core/network/network_module.dart';
import '../services/ai_service.dart';
import '../services/suoke_service.dart';
import '../services/ali_health_service.dart';

class AppBinding extends Bindings {
  @override
  Future<void> dependencies() async {
    // 初始化网络模块
    await NetworkModule.init();

    // 注入 AI 服务
    Get.put(AIService(doubaoClient: Get.find()));

    // 注入 SUOKE 服务
    Get.put(SuokeService());

    // 注入阿里健康服务
    Get.put(AliHealthService(apiClient: Get.find()));
  }
} 