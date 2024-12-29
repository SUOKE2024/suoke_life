import 'package:get/get.dart';
import '../controllers/profile/profile_controller.dart';
import '../../services/features/suoke/suoke_service.dart';

class ProfileBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<ProfileController>(
      () => ProfileController(Get.find<SuokeService>()),
    );
  }
} 