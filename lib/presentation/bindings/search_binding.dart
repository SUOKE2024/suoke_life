import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/search_controller.dart';
import 'package:suoke_life/services/search_history_service.dart';

class SearchBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => SearchHistoryService());
    Get.lazyPut(() => SearchController());
  }
} 