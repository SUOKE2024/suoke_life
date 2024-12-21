import 'package:get/get.dart';
import '../data/services/explore_service.dart';
import '../presentation/controllers/explore_controller.dart';
import '../presentation/controllers/explore_detail_controller.dart';
import '../presentation/controllers/explore_search_controller.dart';

class ExploreBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => ExploreService());
    Get.lazyPut(() => ExploreController());
    Get.lazyPut(() => ExploreDetailController());
    Get.lazyPut(() => ExploreSearchController());
  }
} 