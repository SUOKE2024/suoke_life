import 'package:get/get.dart';
import '../presentation/controllers/group_permissions_controller.dart';
import '../services/group_service.dart';

class GroupPermissionsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<GroupService>(() => GroupService(
      apiClient: Get.find(),
    ));
    
    Get.lazyPut<GroupPermissionsController>(() => GroupPermissionsController(
      groupId: Get.parameters['id']!,
    ));
  }
} 