import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../core/bindings/app_bindings.dart';
import '../routes/app_pages.dart';
import '../routes/app_routes.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'Suoke Life',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      initialBinding: AppBindings(),
      initialRoute: AppPages.INITIAL,
      getPages: AppPages.pages,
      defaultTransition: Transition.fade,
    );
  }
} 