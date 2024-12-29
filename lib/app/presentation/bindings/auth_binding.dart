import 'package:get/get.dart';
import '../presentation/controllers/auth/login_controller.dart';
import '../presentation/controllers/auth/register_controller.dart';
import '../services/auth_service.dart';

class AuthBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<AuthService>(() => AuthService(
      apiClient: Get.find(),
    ));
    
    Get.lazyPut<LoginController>(() => LoginController());
    Get.lazyPut<RegisterController>(() => RegisterController());
  }
} 