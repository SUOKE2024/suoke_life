import 'package:get/get.dart';
import '../presentation/controllers/group_statistics_controller.dart';
import '../services/group_statistics_service.dart';

class GroupStatisticsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<GroupStatisticsService>(() => GroupStatisticsService(
      apiClient: Get.find(),
    ));
    
    Get.lazyPut<GroupStatisticsController>(() => GroupStatisticsController(
      groupId: Get.parameters['id']!,
    ));
  }
} 