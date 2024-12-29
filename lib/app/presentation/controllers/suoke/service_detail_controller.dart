import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/service.dart';

class ServiceDetailController extends GetxController {
  final SuokeService suokeService;
  final Service service;
  final isLoading = false.obs;
  final serviceContent = <Map<String, dynamic>>[].obs;

  ServiceDetailController({
    required this.suokeService,
    required this.service,
  });

  @override
  void onInit() {
    super.onInit();
    loadData();
  }

  Future<void> loadData() async {
    try {
      isLoading.value = true;
      final content = await suokeService.getServiceContent(service.id);
      serviceContent.value = content;
    } catch (e) {
      Get.snackbar('错误', '加载数据失败');
    } finally {
      isLoading.value = false;
    }
  }

  void openServiceItem(Map<String, dynamic> item) {
    switch (service.type) {
      case 'health_survey':
        Get.toNamed('/suoke/survey', arguments: item);
        break;
      case 'agri_product':
        Get.toNamed('/suoke/product', arguments: item);
        break;
      default:
        Get.snackbar('提���', '暂不支持此类服务');
    }
  }

  void showXiaoI() {
    Get.toNamed('/chat/xiaoi', arguments: {
      'service': service,
      'context': 'suoke',
    });
  }
} 