import 'package:get_it/get_it.dart';
import 'package:suoke_life/core/di/modules/network_module.dart';
import 'package:suoke_life/core/di/modules/service_module.dart';
import 'package:suoke_life/core/di/modules/storage_module.dart';
import 'package:suoke_life/core/di/modules/config_module.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:suoke_life/core/di/modules/database_module.dart';

final getIt = GetIt.instance;

Future<void> configureDependencies() async {
  await dotenv.load(fileName: '.env');
  registerConfigModule(getIt);
  registerNetworkModule(getIt);
  registerStorageModule(getIt);
  registerServiceModule(getIt);
  registerDatabaseModule(getIt);
}
