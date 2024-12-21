import 'package:get/get.dart';
import '../controllers/explore_controller.dart';
import '../services/explore_service.dart';

class ExploreBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => ExploreService());
    Get.lazyPut(() => ExploreController());
  }
} 