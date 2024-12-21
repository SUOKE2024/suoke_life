import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'app/routes/app_pages.dart';
import 'app/core/theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 初始化服务
  await initServices();
  
  runApp(const MyApp());
}

Future<void> initServices() async {
  // 初始化核心服务
  await Get.putAsync(() => StorageService().init());
  await Get.putAsync(() => AiService().init());
  // 其他服务初始化
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
    );
  }
}
