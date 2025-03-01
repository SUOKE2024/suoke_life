// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// AutoRouterGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

part of 'app_router.dart';

abstract class _$AppRouter extends RootStackRouter {
  // ignore: unused_element
  _$AppRouter({super.navigatorKey});

  @override
  final Map<String, PageFactory> pagesMap = {
    ExplorePage.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const ExplorePage(),
      );
    },
    ExploreRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const ExploreScreen(),
      );
    },
    HomePage.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const HomePage(),
      );
    },
    HomeRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const HomeScreen(),
      );
    },
    KnowledgeDetailRoute.name: (routeData) {
      final args = routeData.argsAs<KnowledgeDetailRouteArgs>();
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: KnowledgeDetailScreen(
          key: args.key,
          nodeId: args.nodeId,
          nodeType: args.nodeType,
          nodeDescription: args.nodeDescription,
        ),
      );
    },
    KnowledgeGraphRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const KnowledgeGraphScreen(),
      );
    },
    LifePage.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const LifePage(),
      );
    },
    LifeRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const LifeScreen(),
      );
    },
    LoginRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const LoginScreen(),
      );
    },
    MainWrapperRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const MainWrapperScreen(),
      );
    },
    ProfileRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const ProfileScreen(),
      );
    },
    RAGDemoRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const RAGDemoScreen(),
      );
    },
    SuokeRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const SuokeScreen(),
      );
    },
    WelcomeRoute.name: (routeData) {
      return AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const WelcomeScreen(),
      );
    },
  };
}

/// generated route for
/// [ExplorePage]
class ExplorePage extends PageRouteInfo<void> {
  const ExplorePage({List<PageRouteInfo>? children})
      : super(
          ExplorePage.name,
          initialChildren: children,
        );

  static const String name = 'ExplorePage';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [ExploreScreen]
class ExploreRoute extends PageRouteInfo<void> {
  const ExploreRoute({List<PageRouteInfo>? children})
      : super(
          ExploreRoute.name,
          initialChildren: children,
        );

  static const String name = 'ExploreRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [HomePage]
class HomePage extends PageRouteInfo<void> {
  const HomePage({List<PageRouteInfo>? children})
      : super(
          HomePage.name,
          initialChildren: children,
        );

  static const String name = 'HomePage';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [HomeScreen]
class HomeRoute extends PageRouteInfo<void> {
  const HomeRoute({List<PageRouteInfo>? children})
      : super(
          HomeRoute.name,
          initialChildren: children,
        );

  static const String name = 'HomeRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [KnowledgeDetailScreen]
class KnowledgeDetailRoute extends PageRouteInfo<KnowledgeDetailRouteArgs> {
  KnowledgeDetailRoute({
    Key? key,
    required String nodeId,
    required String nodeType,
    required String nodeDescription,
    List<PageRouteInfo>? children,
  }) : super(
          KnowledgeDetailRoute.name,
          args: KnowledgeDetailRouteArgs(
            key: key,
            nodeId: nodeId,
            nodeType: nodeType,
            nodeDescription: nodeDescription,
          ),
          initialChildren: children,
        );

  static const String name = 'KnowledgeDetailRoute';

  static const PageInfo<KnowledgeDetailRouteArgs> page =
      PageInfo<KnowledgeDetailRouteArgs>(name);
}

class KnowledgeDetailRouteArgs {
  const KnowledgeDetailRouteArgs({
    this.key,
    required this.nodeId,
    required this.nodeType,
    required this.nodeDescription,
  });

  final Key? key;

  final String nodeId;

  final String nodeType;

  final String nodeDescription;

  @override
  String toString() {
    return 'KnowledgeDetailRouteArgs{key: $key, nodeId: $nodeId, nodeType: $nodeType, nodeDescription: $nodeDescription}';
  }
}

/// generated route for
/// [KnowledgeGraphScreen]
class KnowledgeGraphRoute extends PageRouteInfo<void> {
  const KnowledgeGraphRoute({List<PageRouteInfo>? children})
      : super(
          KnowledgeGraphRoute.name,
          initialChildren: children,
        );

  static const String name = 'KnowledgeGraphRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [LifePage]
class LifePage extends PageRouteInfo<void> {
  const LifePage({List<PageRouteInfo>? children})
      : super(
          LifePage.name,
          initialChildren: children,
        );

  static const String name = 'LifePage';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [LifeScreen]
class LifeRoute extends PageRouteInfo<void> {
  const LifeRoute({List<PageRouteInfo>? children})
      : super(
          LifeRoute.name,
          initialChildren: children,
        );

  static const String name = 'LifeRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [LoginScreen]
class LoginRoute extends PageRouteInfo<void> {
  const LoginRoute({List<PageRouteInfo>? children})
      : super(
          LoginRoute.name,
          initialChildren: children,
        );

  static const String name = 'LoginRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [MainWrapperScreen]
class MainWrapperRoute extends PageRouteInfo<void> {
  const MainWrapperRoute({List<PageRouteInfo>? children})
      : super(
          MainWrapperRoute.name,
          initialChildren: children,
        );

  static const String name = 'MainWrapperRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [ProfileScreen]
class ProfileRoute extends PageRouteInfo<void> {
  const ProfileRoute({List<PageRouteInfo>? children})
      : super(
          ProfileRoute.name,
          initialChildren: children,
        );

  static const String name = 'ProfileRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [RAGDemoScreen]
class RAGDemoRoute extends PageRouteInfo<void> {
  const RAGDemoRoute({List<PageRouteInfo>? children})
      : super(
          RAGDemoRoute.name,
          initialChildren: children,
        );

  static const String name = 'RAGDemoRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [SuokeScreen]
class SuokeRoute extends PageRouteInfo<void> {
  const SuokeRoute({List<PageRouteInfo>? children})
      : super(
          SuokeRoute.name,
          initialChildren: children,
        );

  static const String name = 'SuokeRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}

/// generated route for
/// [WelcomeScreen]
class WelcomeRoute extends PageRouteInfo<void> {
  const WelcomeRoute({List<PageRouteInfo>? children})
      : super(
          WelcomeRoute.name,
          initialChildren: children,
        );

  static const String name = 'WelcomeRoute';

  static const PageInfo<void> page = PageInfo<void>(name);
}
