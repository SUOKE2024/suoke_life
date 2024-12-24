import 'package:get/get.dart';
import '../../routes/app_routes.dart';

class ProfileController extends GetxController {
  void navigateToDevices() => Get.toNamed(Routes.SETTINGS);
  void navigateToHelp() => Get.toNamed(Routes.SETTINGS);
  void navigateToAbout() => Get.toNamed(Routes.SETTINGS);
  void navigateToSettings() => Get.toNamed(Routes.SETTINGS);
  void navigateToAccount() => Get.toNamed(Routes.SETTINGS);
  void navigateToPrivacy() => Get.toNamed(Routes.SETTINGS);

  Future<void> logout() async {
    // TODO: 实现登出逻辑
    Get.offAllNamed(Routes.LOGIN);
  }
} 