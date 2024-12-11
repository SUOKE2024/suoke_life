import 'package:get/get.dart';
import 'laoke_controller.dart';

class LaokeBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => LaokeController());
  }
} 