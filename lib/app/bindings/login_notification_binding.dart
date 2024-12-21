import 'package:get/get.dart';
import '../presentation/controllers/login_notification_controller.dart';

class LoginNotificationBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<LoginNotificationController>(() => LoginNotificationController());
  }
} 