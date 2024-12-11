import 'package:get/get.dart';
import '../../modules/chat/chat_module.dart';
import '../../modules/ai/ai_module.dart';
// 导入其他模块...

/// 应用路由
abstract class AppPages {
  static final pages = [
    GetPage(
      name: Routes.HOME,
      page: () => const HomePage(),
      binding: HomeBinding(),
      children: [
        GetPage(
          name: Routes.PROFILE,
          page: () => const ProfilePage(),
          binding: ProfileBinding(),
        ),
      ],
    ),
  ];

  static void configureRoutes() {
    Get.config(
      enableLog: true,
      defaultTransition: Transition.fade,
      defaultOpaqueRoute: true,
      defaultPopGesture: true,
    );
  }
} 