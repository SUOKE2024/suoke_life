import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:suoke_life_app_app/core/navigation/app_navigator.dart';
import 'package:suoke_life_app_app/features/auth/auth.dart';
import 'package:suoke_life_app_app/features/explore/explore.dart';
import 'package:suoke_life_app_app/features/home/home.dart';
import 'package:suoke_life_app_app/features/life/life.dart';
import 'package:suoke_life_app_app/features/profile/profile.dart';
import 'package:suoke_life_app_app/features/suoke/suoke.dart';

part 'app_router.gr.dart';

@AutoRouterConfig(
  replaceInRouteName: 'Page,Route',
)
class AppRouter extends _$AppRouter with AppNavigator {
  @override
  List<AutoRoute> get routes => [
        AutoRoute(page: WelcomeRoute.page, initial: true),
        AutoRoute(page: LoginRoute.page),
        AutoRoute(page: RegisterRoute.page),
        AutoRoute(page: HomeRoute.page),
        AutoRoute(page: SuokeRoute.page),
        AutoRoute(page: ExploreRoute.page),
        AutoRoute(page: LifeRoute.page),
        AutoRoute(page: ProfileRoute.page),
        AutoRoute(page: SettingsRoute.page),
        AutoRoute(page: EditProfileRoute.page),
        AutoRoute(page: AdminDashboardRoute.page),
        AutoRoute(page: ChatInteractionRoute.page),
      ];
}
