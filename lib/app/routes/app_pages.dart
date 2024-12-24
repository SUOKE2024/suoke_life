import 'package:get/get.dart';
import '../presentation/pages/home/home_page.dart';
import '../presentation/pages/profile/profile_page.dart';
import '../presentation/pages/settings/settings_page.dart';
import 'app_routes.dart';

abstract class AppPages {
  static const INITIAL = Routes.HOME;

  static final routes = [
    GetPage(
      name: Routes.HOME,
      page: () => const HomePage(),
    ),
    GetPage(
      name: Routes.SETTINGS,
      page: () => const SettingsPage(),
    ),
  ];
} 