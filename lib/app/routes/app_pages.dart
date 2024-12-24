import 'package:get/get.dart';
import '../presentation/pages/home/home_page.dart';
import '../presentation/pages/suoke/suoke_page.dart';
import '../presentation/pages/explore/explore_page.dart';
import '../presentation/pages/life/life_page.dart';
import '../presentation/pages/profile/profile_page.dart';
import '../presentation/pages/settings/settings_page.dart';
import '../presentation/pages/admin/admin_page.dart';

part 'app_routes.dart';

class AppPages {
  static final routes = [
    // 主页面
    GetPage(
      name: Routes.HOME,
      page: () => const HomePage(),
      binding: HomeBinding(),
    ),
    GetPage(
      name: Routes.SUOKE,
      page: () => const SuokePage(),
      binding: SuokeBinding(),
    ),
    GetPage(
      name: Routes.EXPLORE,
      page: () => const ExplorePage(),
      binding: ExploreBinding(),
    ),
    GetPage(
      name: Routes.LIFE,
      page: () => const LifePage(),
      binding: LifeBinding(),
    ),
    GetPage(
      name: Routes.PROFILE,
      page: () => const ProfilePage(),
      binding: ProfileBinding(),
    ),

    // 设置相关
    GetPage(
      name: Routes.SETTINGS,
      page: () => const SettingsPage(),
      binding: SettingsBinding(),
      children: [
        GetPage(
          name: '/device',
          page: () => const DeviceSettingsPage(),
        ),
        GetPage(
          name: '/privacy',
          page: () => const PrivacySettingsPage(),
        ),
        GetPage(
          name: '/notification',
          page: () => const NotificationSettingsPage(),
        ),
        GetPage(
          name: '/language',
          page: () => const LanguageSettingsPage(),
        ),
        GetPage(
          name: '/ai',
          page: () => const AiSettingsPage(),
        ),
        GetPage(
          name: '/voice',
          page: () => const VoiceSettingsPage(),
        ),
      ],
    ),

    // 系统管理
    GetPage(
      name: Routes.ADMIN,
      page: () => const AdminPage(),
      binding: AdminBinding(),
      children: [
        GetPage(
          name: '/experts',
          page: () => const ExpertManagementPage(),
        ),
        GetPage(
          name: '/services',
          page: () => const ServiceManagementPage(),
        ),
        GetPage(
          name: '/products',
          page: () => const ProductManagementPage(),
        ),
        GetPage(
          name: '/ai',
          page: () => const AiModelManagementPage(),
        ),
        GetPage(
          name: '/api',
          page: () => const ApiManagementPage(),
        ),
      ],
    ),

    // 功能页面
    GetPage(
      name: Routes.HEALTH_SURVEY,
      page: () => const HealthSurveyPage(),
    ),
    GetPage(
      name: Routes.LIFE_RECORD,
      page: () => const LifeRecordPage(),
    ),
    GetPage(
      name: Routes.FEEDBACK,
      page: () => const FeedbackPage(),
    ),
  ];
} 