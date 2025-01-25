import 'package:get_it/get_it.dart';
import 'package:suoke_life/core/di/modules/network_module.dart';
import 'package:suoke_life/core/di/modules/service_module.dart';
import 'package:suoke_life/core/di/modules/storage_module.dart';
import 'package:suoke_life/core/di/modules/config_module.dart';

final getIt = GetIt.instance;

void configureDependencies() {
  registerConfigModule(getIt);
  registerNetworkModule(getIt);
  registerStorageModule(getIt);
  registerServiceModule(getIt);
} 