import 'package:get_it/get_it.dart';

final GetIt getIt = GetIt.instance;

void setupLocator() {
  // Register services
  getIt.registerLazySingleton<DatabaseHelper>(() => DatabaseHelper());
  getIt.registerLazySingleton<AuthService>(() => AuthServiceImpl(getIt<LocalStorageService>(), getIt<PrivacyService>()));
  // Add other service registrations here
}
