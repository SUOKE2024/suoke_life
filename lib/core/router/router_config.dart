import 'package:auto_route/auto_route.dart';
import 'package:suoke_life_app_app_app/app/presentation/pages/pages.dart';

part 'router_config.g.dart';

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
  ];
} 