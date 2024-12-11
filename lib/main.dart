import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'app/core/di/dependency_manager.dart';
import 'app/core/base/app_module.dart';
import 'app/core/services/logger_service.dart';

void main() async {
  try {
    WidgetsFlutterBinding.ensureInitialized();

    // Initialize app modules
    await initializeApp();

    // Run app
    runApp(const MyApp());
  } catch (e) {
    LoggerService.error('Failed to start application', error: e);
    runApp(const ErrorApp()); // 显示错误页面
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'SuoKe Life',
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      initialRoute: AppPages.initial,
      getPages: AppPages.routes,
      initialBinding: AppBinding(),
      locale: TranslationService.locale,
      fallbackLocale: TranslationService.fallbackLocale,
      translations: TranslationService(),
      onInit: () {
        LoggerService.info('Application UI initialized');
      },
    );
  }
}
