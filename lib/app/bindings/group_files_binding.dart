import 'package:get/get.dart';
import '../presentation/controllers/group_files_controller.dart';
import '../services/group_files_service.dart';

class GroupFilesBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<GroupFilesService>(() => GroupFilesService(
      apiClient: Get.find(),
    ));
    
    Get.lazyPut<GroupFilesController>(() => GroupFilesController(
      groupId: Get.parameters['id']!,
    ));
  }
} 