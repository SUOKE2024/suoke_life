import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';

import '../pages/main/main_page.dart';
import '../pages/home/home_page.dart';
import '../pages/suoke/suoke_page.dart';
import '../pages/explore/explore_page.dart';
import '../pages/life/life_page.dart';
import '../pages/profile/profile_page.dart';

part 'app_pages.gr.dart';

@AutoRouterConfig(replaceInRouteName: 'Page,Route')
class AppRouter extends _$AppRouter {
  @override
  List<AutoRoute> get routes => [
    AutoRoute(
      path: '/',
      page: MainRoute.page,
      initial: true,
      children: [
        AutoRoute(path: 'home', page: HomeRoute.page),
        AutoRoute(path: 'suoke', page: SuokeRoute.page),
        AutoRoute(path: 'explore', page: ExploreRoute.page),
        AutoRoute(path: 'life', page: LifeRoute.page),
        AutoRoute(path: 'profile', page: ProfileRoute.page),
      ],
    ),
  ];

  @override
  RouteType get defaultRouteType => const RouteType.material();
} 