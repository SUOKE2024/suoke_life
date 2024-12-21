import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../core/theme/app_theme.dart';
import '../routes/app_pages.dart';
import '../core/bindings/app_bindings.dart';

class App extends StatelessWidget {
  const App({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'SuoKe Life',
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.system,
      initialRoute: AppPages.INITIAL,
      getPages: AppPages.routes,
      initialBinding: AppBindings(),
      defaultTransition: Transition.cupertino,
      debugShowCheckedModeBanner: false,
    );
  }
} 