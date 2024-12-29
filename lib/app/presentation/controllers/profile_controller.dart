import 'package:get/get.dart';
import '../routes/app_routes.dart';

class ProfileController extends GetxController {
  void navigateToSettings() => Get.toNamed(Routes.SETTINGS);
  
  Future<void> logout() async {
    // TODO: 实现登出逻辑
    Get.offAllNamed(Routes.LOGIN);
  }
} 