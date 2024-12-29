import 'package:get/get.dart';
import '../presentation/controllers/group_member_analysis_controller.dart';
import '../services/group_statistics_service.dart';

class GroupMemberAnalysisBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<GroupStatisticsService>(() => GroupStatisticsService(
      apiClient: Get.find(),
    ));
    
    Get.lazyPut<GroupMemberAnalysisController>(() => GroupMemberAnalysisController(
      groupId: Get.parameters['id']!,
    ));
  }
} 