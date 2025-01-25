import 'package:auto_route/auto_route.dart';
import '../presentation/pages/home/home_page.dart';
import '../presentation/pages/chat/chat_detail_page.dart';
import '../presentation/pages/profile/profile_page.dart';
import '../presentation/pages/auth/member_register_page.dart';
import '../presentation/pages/auth/expert_register_page.dart';
import '../presentation/pages/social/add_friend_page.dart';
import '../presentation/pages/social/create_group_page.dart';
import '../presentation/pages/consultation/consultation_page.dart';
import '../presentation/pages/scanner/scanner_page.dart';
import '../presentation/pages/payment/payment_page.dart';

@AutoRouterConfig()
class AppRouter extends $AppRouter {
  @override
  List<AutoRoute> get routes => [
    AutoRoute(
      path: '/',
      page: HomeRoute.page,
      initial: true,
    ),
    AutoRoute(
      path: '/chat/:id',
      page: ChatDetailRoute.page,
    ),
    AutoRoute(
      path: '/profile',
      page: ProfileRoute.page,
    ),
    AutoRoute(
      path: '/member-register',
      page: MemberRegisterPage,
    ),
    AutoRoute(
      path: '/expert-register',
      page: ExpertRegisterPage,
    ),
    AutoRoute(
      path: '/add-friend',
      page: AddFriendPage,
    ),
    AutoRoute(
      path: '/create-group',
      page: CreateGroupPage,
    ),
    AutoRoute(
      path: '/consultation',
      page: ConsultationPage,
    ),
    AutoRoute(
      path: '/scanner',
      page: ScannerPage,
    ),
    AutoRoute(
      path: '/payment',
      page: PaymentPage,
    ),
  ];
} 