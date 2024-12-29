import 'package:get/get.dart';
import '../controllers/explore/explore_controller.dart';
import '../../services/features/suoke/suoke_service.dart';

class ExploreBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<ExploreController>(
      () => ExploreController(Get.find<SuokeService>()),
    );
  }
} 