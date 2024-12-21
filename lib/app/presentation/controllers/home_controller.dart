import 'package:get/get.dart';
import '../../data/models/health_record.dart';
import '../../data/models/life_record.dart';
import '../../services/life_service.dart';

class HomeController extends GetxController {
  final LifeService _lifeService = Get.find();
  
  final currentIndex = 0.obs;
  final healthData = Rx<HealthRecord?>(null);
  final lifeRecords = <LifeRecord>[].obs;

  @override
  void onInit() {
    super.onInit();
    loadData();
  }

  Future<void> loadData() async {
    try {
      final records = await _lifeService.getLifeRecords();
      lifeRecords.value = records;
      
      // TODO: 加载健康数据
    } catch (e) {
      Get.snackbar('错误', '加载数据失败');
    }
  }

  void changePage(int index) {
    currentIndex.value = index;
    switch (index) {
      case 0: // 首页
        break;
      case 1: // SUOKE
        Get.toNamed('/suoke');
        break;
      case 2: // 探索
        Get.toNamed('/explore');
        break;
      case 3: // LIFE
        Get.toNamed('/life');
        break;
      case 4: // 我的
        Get.toNamed('/profile');
        break;
    }
  }
} 