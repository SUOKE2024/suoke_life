import 'package:get/get.dart';
import '../controllers/home/home_controller.dart';
import '../services/features/suoke/suoke_service.dart';
import '../services/features/ai/doubao_service.dart';
import '../services/features/ai/assistants/xiaoi_service.dart';
import '../services/features/chat/chat_service.dart';

class InitialBinding extends Bindings {
  @override
  void dependencies() {
    // 核心服务
    Get.put<SuokeService>(SuokeServiceImpl());
    
    // 控制器
    Get.put<HomeController>(HomeController());
    Get.lazyPut<ChatController>(() => ChatController());
    Get.lazyPut<SuokeController>(() => SuokeController());
    Get.lazyPut<ExploreController>(() => ExploreController());
    Get.lazyPut<LifeController>(() => LifeController());
    Get.lazyPut<ProfileController>(() => ProfileController());
  }
} 