import 'package:get/get.dart';
import '../../pages/app.dart';
import '../../pages/home/home_page.dart';
import '../../pages/explore/explore_page.dart';
import '../../pages/service/service_page.dart';
import '../../pages/community/community_page.dart';
import '../../pages/profile/profile_page.dart';
import '../../pages/games/leaderboard/leaderboard_page.dart';
import '../../pages/games/leaderboard/leaderboard_binding.dart';
import '../../pages/chat/xiaoi/xiaoi_chat_page.dart';
import '../../pages/chat/xiaoi/xiaoi_binding.dart';
import '../../pages/chat/laoke/laoke_chat_page.dart';
import '../../pages/chat/laoke/laoke_binding.dart';
import '../../pages/test/ai_test_page.dart';
import '../../pages/service/service_binding.dart';
import '../../core/bindings/explore_binding.dart';
import 'route_paths.dart';

class AppPages {
  static final pages = [
    GetPage(
      name: '/',
      page: () => const AppPage(),
    ),
    // 主导航
    GetPage(
      name: RoutePaths.home,
      page: () => const HomePage(),
    ),
    GetPage(
      name: RoutePaths.explore,
      page: () => const ExplorePage(),
      binding: ExploreBinding(),
    ),
    GetPage(
      name: RoutePaths.service,
      page: () => const ServicePage(),
      binding: ServiceBinding(),
    ),
    GetPage(
      name: RoutePaths.community,
      page: () => const CommunityPage(),
    ),
    GetPage(
      name: RoutePaths.profile,
      page: () => const ProfilePage(),
    ),

    // 聊天相关
    GetPage(
      name: RoutePaths.xiaoiChat,
      page: () => const XiaoiChatPage(),
      binding: XiaoiBinding(),
    ),
    GetPage(
      name: RoutePaths.laokeChat,
      page: () => const LaokeChatPage(),
      binding: LaokeBinding(),
    ),
    // TODO: 添加其他聊天页面路由

    // 游戏相关
    GetPage(
      name: RoutePaths.gameLeaderboard,
      page: () => const LeaderboardPage(),
      binding: LeaderboardBinding(),
    ),

    // 测试页面
    GetPage(
      name: RoutePaths.aiTest,
      page: () => const AITestPage(),
    ),
  ];
}
