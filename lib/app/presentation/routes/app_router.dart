import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import '../pages/home/home_page.dart';
import '../pages/chat/chat_detail_page.dart';
import '../pages/profile/profile_page.dart';
import '../pages/settings/settings_page.dart';
import '../pages/about/about_page.dart';
import '../pages/help/help_page.dart';

part 'app_router.gr.dart';

@AutoRouterConfig()
class AppRouter extends _$AppRouter {
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
          path: '/settings',
          page: SettingsRoute.page,
        ),
        AutoRoute(
          path: '/about',
          page: AboutRoute.page,
        ),
        AutoRoute(
          path: '/help',
          page: HelpRoute.page,
        ),
      ];
} 