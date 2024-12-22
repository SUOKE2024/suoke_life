import 'package:get/get.dart';
import '../controllers/profile_controller.dart';
import '../../services/auth_service.dart';

class ProfileBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => ProfileController());
  }
} 