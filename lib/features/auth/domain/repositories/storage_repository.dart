import 'package:get_it/get_it.dart';
import '../services/infrastructure/database_service.dart';
import '../services/infrastructure/database_service_impl.dart';
import '../services/infrastructure/local_storage_service.dart';
import '../services/infrastructure/local_storage_service_impl.dart';

void registerStorageModule(GetIt getIt) {
  // 数据库服务
  getIt.registerLazySingleton<DatabaseService>(
    () => DatabaseServiceImpl() as DatabaseService,
  );

  // 本地存储服务
  getIt.registerLazySingleton<LocalStorageService>(
    () => LocalStorageServiceImpl(getIt<DatabaseService>())
        as LocalStorageService,
  );
}
