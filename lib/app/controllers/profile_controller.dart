import 'package:get/get.dart';
import '../services/auth/auth_service.dart';

class ProfileController extends GetxController {
  final AuthService _authService = Get.find();
  
  Future<void> logout() async {
    try {
      await _authService.logout();
      Get.offAllNamed('/login');
    } catch (e) {
      Get.snackbar('错误', '登出失败');
    }
  }
} 