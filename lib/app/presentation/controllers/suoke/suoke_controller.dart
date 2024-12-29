import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/service.dart';

class SuokeController extends GetxController {
  final SuokeService suokeService;
  final services = <Service>[].obs;
  final isLoading = false.obs;

  SuokeController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    loadServices();
  }

  Future<void> loadServices() async {
    try {
      isLoading.value = true;
      final result = await suokeService.getServices();
      services.value = result;
    } catch (e) {
      Get.snackbar('错误', '加载服务列表失败');
    } finally {
      isLoading.value = false;
    }
  }

  void openService(Service service) {
    Get.toNamed('/service/${service.id}', arguments: service);
  }
} 