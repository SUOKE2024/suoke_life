import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';
import 'injection.config.dart';

final getIt = GetIt.instance;

@InjectableInit()
void configureDependencies() => getIt.init();

@module
abstract class RegisterModule {
  @singleton
  DatabaseHelper get databaseHelper => DatabaseHelper();
  
  @singleton
  NetworkService get networkService => NetworkService();
  
  @singleton
  StorageService get storageService => StorageService();
} 