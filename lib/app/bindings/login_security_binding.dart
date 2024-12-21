import 'package:get/get.dart';
import '../presentation/controllers/login_security_controller.dart';
import '../services/login_security_service.dart';
import '../services/biometric_service.dart';

class LoginSecurityBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<LoginSecurityController>(() => LoginSecurityController());
  }
} 