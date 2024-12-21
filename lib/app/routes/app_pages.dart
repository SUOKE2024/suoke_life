import 'package:get/get.dart';
import '../presentation/pages/home/home_page.dart';
import '../presentation/pages/ai/ai_chat_page.dart';
import '../presentation/pages/life/life_page.dart';
import '../presentation/pages/explore/explore_page.dart';

part 'app_routes.dart';

class AppPages {
  static const INITIAL = Routes.HOME;

  static final routes = [
    GetPage(
      name: Routes.HOME,
      page: () => const HomePage(),
      binding: HomeBinding(),
    ),
    GetPage(
      name: Routes.AI_CHAT,
      page: () => const AiChatPage(),
      binding: AiChatBinding(),
    ),
    GetPage(
      name: Routes.LIFE,
      page: () => const LifePage(),
      binding: LifeBinding(),
    ),
    GetPage(
      name: Routes.EXPLORE,
      page: () => const ExplorePage(),
      binding: ExploreBinding(),
    ),
  ];
} 