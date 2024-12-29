import 'package:get/get.dart';
import '../presentation/pages/home/home_page.dart';
import '../presentation/pages/chat/chat_page.dart';
import '../presentation/pages/chat/chat_detail_page.dart';
import '../presentation/pages/suoke/suoke_page.dart';
import '../presentation/pages/suoke/service_detail_page.dart';
import '../presentation/pages/explore/explore_page.dart';
import '../presentation/pages/explore/topic_detail_page.dart';
import '../presentation/pages/life/life_page.dart';
import '../presentation/pages/life/advice_detail_page.dart';
import '../presentation/pages/profile/profile_page.dart';
import '../presentation/pages/profile/settings_page.dart';
import '../presentation/bindings/home_binding.dart';
import '../presentation/bindings/chat_binding.dart';
import '../presentation/bindings/chat_detail_binding.dart';
import '../presentation/bindings/suoke_binding.dart';
import '../presentation/bindings/service_detail_binding.dart';
import '../presentation/bindings/explore_binding.dart';
import '../presentation/bindings/topic_detail_binding.dart';
import '../presentation/bindings/life_binding.dart';
import '../presentation/bindings/advice_detail_binding.dart';
import '../presentation/bindings/profile_binding.dart';
import '../presentation/bindings/settings_binding.dart';

class AppPages {
  static final routes = [
    GetPage(
      name: '/',
      page: () => const HomePage(),
      binding: HomeBinding(),
      children: [
        GetPage(
          name: '/chat',
          page: () => const ChatPage(),
          binding: ChatBinding(),
          children: [
            GetPage(
              name: '/detail/:id',
              page: () => const ChatDetailPage(),
              binding: ChatDetailBinding(),
            ),
          ],
        ),
        GetPage(
          name: '/suoke',
          page: () => const SuokePage(),
          binding: SuokeBinding(),
          children: [
            GetPage(
              name: '/service/:id',
              page: () => const ServiceDetailPage(),
              binding: ServiceDetailBinding(),
            ),
          ],
        ),
        GetPage(
          name: '/explore',
          page: () => const ExplorePage(),
          binding: ExploreBinding(),
          children: [
            GetPage(
              name: '/topic/:id',
              page: () => const TopicDetailPage(),
              binding: TopicDetailBinding(),
            ),
          ],
        ),
        GetPage(
          name: '/life',
          page: () => const LifePage(),
          binding: LifeBinding(),
          children: [
            GetPage(
              name: '/advice/:id',
              page: () => const AdviceDetailPage(),
              binding: AdviceDetailBinding(),
            ),
          ],
        ),
        GetPage(
          name: '/profile',
          page: () => const ProfilePage(),
          binding: ProfileBinding(),
          children: [
            GetPage(
              name: '/settings',
              page: () => const SettingsPage(),
              binding: SettingsBinding(),
            ),
          ],
        ),
      ],
    ),
  ];
} 