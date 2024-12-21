import 'package:get/get.dart';
import '../controllers/network_history_controller.dart';

class NetworkHistoryBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<NetworkHistoryController>(() => NetworkHistoryController());
  }
} 