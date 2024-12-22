import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'app/routes/app_pages.dart';
import 'app/core/theme/app_theme.dart';
import 'app/core/di/dependency_injection.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 设置 Get 测试模式
  Get.testMode = true;
  
  // 初始化依赖
  await DependencyInjection.init();
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'SuoKe Life',
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      initialRoute: AppPages.INITIAL,
      getPages: AppPages.routes,
      locale: const Locale('zh', 'CN'),
      fallbackLocale: const Locale('en', 'US'),
      defaultTransition: Transition.fade,
      debugShowCheckedModeBanner: false,
    );
  }
}
