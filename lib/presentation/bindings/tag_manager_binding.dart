import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/tag_manager_controller.dart';

class TagManagerBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<TagManagerController>(() => TagManagerController());
  }
} 