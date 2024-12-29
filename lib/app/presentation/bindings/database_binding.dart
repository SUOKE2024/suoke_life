import 'package:get/get.dart';
import '../data/providers/database_provider.dart';
import '../data/repositories/record_repository.dart';
import '../data/repositories/tag_repository.dart';
import '../controllers/records_controller.dart';
import '../controllers/tag_controller.dart';

class DatabaseBinding extends Bindings {
  @override
  void dependencies() {
    // 注册数据库提供者
    Get.lazyPut<DatabaseProvider>(() => DatabaseProvider());

    // 注册仓库
    Get.lazyPut<RecordRepository>(
      () => RecordRepository(Get.find<DatabaseProvider>()),
    );
    Get.lazyPut<TagRepository>(
      () => TagRepository(Get.find<DatabaseProvider>()),
    );

    // 注册控制器
    Get.lazyPut<RecordsController>(
      () => RecordsController(Get.find<RecordRepository>()),
    );
    Get.lazyPut<TagController>(
      () => TagController(Get.find<TagRepository>()),
    );
  }
} 