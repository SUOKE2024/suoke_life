import 'package:get/get.dart';
import '../controllers/life/life_controller.dart';
import '../../services/features/suoke/suoke_service.dart';

class LifeBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<LifeController>(
      () => LifeController(Get.find<SuokeService>()),
    );
  }
} 