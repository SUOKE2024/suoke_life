import 'package:get/get.dart';
import '../database/database_helper.dart';
import '../../services/features/chat/chat_service.dart';
import '../../services/features/suoke/suoke_service.dart';
import '../../presentation/controllers/home/home_controller.dart';

class AppBindings extends Bindings {
  @override
  void dependencies() {
    // 注册数据库
    Get.put<DatabaseHelper>(
      DatabaseHelper(),
      permanent: true,
    );

    // 注册 SuokeService
    Get.put<SuokeService>(
      SuokeServiceImpl(),
      permanent: true,
    );

    // 注册 ChatService
    Get.put<ChatService>(
      ChatService(),
      permanent: true,
    );

    // 注册 HomeController
    Get.lazyPut<HomeController>(
      () => HomeController(
        suokeService: Get.find<SuokeService>(),
      ),
    );
  }
} 