import 'package:get/get.dart';
import '../../services/suoke_service.dart';
import '../../services/ai_service.dart';
import '../../data/models/service.dart';

class SuokeController extends GetxController {
  final SuokeService _suokeService;
  final AIService _aiService;
  
  final healthServices = <Service>[].obs;
  final agriServices = <Service>[].obs;
  final isLoading = false.obs;

  SuokeController({
    required SuokeService suokeService,
    required AIService aiService,
  }) : _suokeService = suokeService,
       _aiService = aiService;

  @override
  void onInit() {
    super.onInit();
    _loadServices();
  }

  Future<void> _loadServices() async {
    isLoading.value = true;
    try {
      // 加载健康服务
      final healthData = await _suokeService.getHealthServices();
      healthServices.value = healthData;

      // 加载农产品服务
      final agriData = await _suokeService.getAgriProducts();
      agriServices.value = agriData;
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> refreshServices() async {
    await _loadServices();
  }

  void showServiceMenu() {
    Get.bottomSheet(
      Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.add_business),
              title: const Text('添加第三方服务'),
              onTap: () {
                Get.back();
                Get.toNamed('/services/add');
              },
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('服务设置'),
              onTap: () {
                Get.back();
                Get.toNamed('/services/settings');
              },
            ),
          ],
        ),
      ),
    );
  }

  void openService(Service service) async {
    switch (service.type) {
      case 'health_survey':
        Get.toNamed('/services/health/survey');
        break;
      case 'tcm_constitution':
        Get.toNamed('/services/health/tcm');
        break;
      case 'agri_product':
        Get.toNamed('/services/agri/products');
        break;
      default:
        Get.toNamed('/services/${service.type}');
    }
  }

  void openAIChat(String aiId) {
    Get.toNamed('/chat/ai/$aiId');
  }
} 