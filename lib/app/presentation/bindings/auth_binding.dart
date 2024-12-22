import 'package:get/get.dart';
import '../controllers/auth_controller.dart';
import '../../services/auth_service.dart';

class AuthBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => AuthController(
      authService: Get.find<AuthService>(),
    ));
  }
} 