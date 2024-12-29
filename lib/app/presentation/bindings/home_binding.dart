import 'package:get/get.dart';
import '../controllers/home/home_controller.dart';
import '../../services/features/suoke/suoke_service.dart';
import '../controllers/chat/chat_controller.dart';
import '../controllers/suoke/suoke_controller.dart';
import '../controllers/explore/explore_controller.dart';
import '../controllers/life/life_controller.dart';
import '../controllers/profile/profile_controller.dart';

class HomeBinding extends Bindings {
  @override
  void dependencies() {
    // 注册主控制器
    Get.lazyPut<HomeController>(
      () => HomeController(Get.find<SuokeService>()),
    );

    // 注册子页面控制器
    Get.lazyPut<ChatController>(
      () => ChatController(Get.find<SuokeService>()),
    );
    
    Get.lazyPut<SuokeController>(
      () => SuokeController(Get.find<SuokeService>()),
    );
    
    Get.lazyPut<ExploreController>(
      () => ExploreController(Get.find<SuokeService>()),
    );
    
    Get.lazyPut<LifeController>(
      () => LifeController(Get.find<SuokeService>()),
    );
    
    Get.lazyPut<ProfileController>(
      () => ProfileController(Get.find<SuokeService>()),
    );
  }
} 