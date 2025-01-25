import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import '../di/injection.dart';
import 'router_config.dart';

@AutoRouterConfig()
class AppRouter extends $AppRouter {
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
    AutoRoute(
      path: '/chat/:assistantId',
      page: ChatRoute.page,
    ),
    AutoRoute(
      path: '/service/:serviceId',
      page: ServiceDetailRoute.page,
    ),
  ];

  static AppRouter get instance => getIt<AppRouter>();
} 