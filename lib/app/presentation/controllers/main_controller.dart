import 'package:get/get.dart';
import '../../services/auth_service.dart';

class MainController extends GetxController {
  final _authService = Get.find<AuthService>();
  
  final currentIndex = 0.obs;

  void changePage(int index) {
    currentIndex.value = index;
  }

  @override
  void onInit() {
    super.onInit();
    // 延迟检查登录状态
    Future.delayed(Duration.zero, () {
      if (!_authService.isLoggedIn.value) {
        Get.offAllNamed('/login');
      }
    });
  }
} 