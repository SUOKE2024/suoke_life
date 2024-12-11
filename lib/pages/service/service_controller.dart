import 'package:get/get.dart';
import '../../core/routes/route_paths.dart';
import 'service_model.dart';

class ServiceController extends GetxController {
  final RxList<ServiceModel> services = <ServiceModel>[].obs;

  @override
  void onInit() {
    super.onInit();
    _loadServices();
  }

  void _loadServices() {
    // 模拟数据，实际应从API获取
    services.value = [
      ServiceModel(
        title: '第三方API服务',
        description: '专业API服务接入',
        coverImage: 'https://picsum.photos/400/300?random=1',
        route: RoutePaths.apiService,
        popularity: 95,
        visits: '1.2k',
        rating: 4.8,
      ),
      ServiceModel(
        title: '索克定制',
        description: '个性化定制服务',
        coverImage: 'https://picsum.photos/400/300?random=2',
        route: RoutePaths.customService,
        popularity: 88,
        visits: '856',
        rating: 4.6,
      ),
      ServiceModel(
        title: '供应链入口',
        description: '一站式供应链服务',
        coverImage: 'https://picsum.photos/400/300?random=3',
        route: RoutePaths.supplyChain,
        popularity: 92,
        visits: '723',
        rating: 4.7,
      ),
    ];
  }
} 