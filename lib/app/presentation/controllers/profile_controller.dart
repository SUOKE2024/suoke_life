import 'package:get/get.dart';
import '../../data/models/user_info.dart';
import '../../routes/app_routes.dart';

class ProfileController extends GetxController {
  final userInfo = UserInfo(
    id: '1',
    name: '测试用户',
    role: '普通用户',
  ).obs;
  
  void updateAvatar() {
    // TODO: 实现头像更新
  }
  
  void updateName() {
    // TODO: 实现名称更新
  }
  
  void navigateToSettings() {
    Get.toNamed(AppRoutes.SETTINGS);
  }
  
  void navigateToAccount() {
    Get.toNamed(AppRoutes.ACCOUNT);
  }
  
  void navigateToPrivacy() {
    Get.toNamed(AppRoutes.PRIVACY);
  }
  
  void navigateToDevices() {
    Get.toNamed(AppRoutes.DEVICES);
  }
  
  void navigateToHelp() {
    Get.toNamed(AppRoutes.HELP);
  }
  
  void navigateToAbout() {
    Get.toNamed(AppRoutes.ABOUT);
  }
  
  Future<void> logout() async {
    final result = await Get.dialog<bool>(
      AlertDialog(
        title: const Text('确认退出'),
        content: const Text('确定要退出登录吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(result: false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Get.back(result: true),
            child: const Text('确定'),
          ),
        ],
      ),
    );
    
    if (result == true) {
      // TODO: 实现退出登录逻辑
      Get.offAllNamed(AppRoutes.LOGIN);
    }
  }
} 