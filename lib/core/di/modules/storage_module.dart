import 'package:get_it/get_it.dart';
import '../../services/infrastructure/database_service.dart';
import '../../services/infrastructure/database_service_impl.dart';
import '../../services/infrastructure/local_storage_service.dart';
import '../../services/infrastructure/local_storage_service_impl.dart';

// 注册存储模块的依赖
//
// 在这里注册 DatabaseService, SharedPreferencesService 等存储相关的服务
void registerStorageModule(GetIt getIt) {
  // 注册 DatabaseService 为懒加载单例
  getIt.registerLazySingleton<DatabaseService>(() => DatabaseServiceImpl());
  // 注册 LocalStorageService 为懒加载单例，并注入 DatabaseService
  getIt.registerLazySingleton<LocalStorageService>(() => LocalStorageServiceImpl(getIt<DatabaseService>()));
}
