// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// AutoRouterGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:auto_route/auto_route.dart' as _i12;
import 'package:flutter/material.dart' as _i13;
import 'package:suoke_life/core/router/app_router.dart' as _i7;
import 'package:suoke_life/presentation/screens/ai/rag_demo_screen.dart' as _i9;
import 'package:suoke_life/presentation/screens/auth/login_screen.dart' as _i6;
import 'package:suoke_life/presentation/screens/explore/explore_screen.dart'
    as _i1;
import 'package:suoke_life/presentation/screens/home/home_screen.dart' as _i2;
import 'package:suoke_life/presentation/screens/knowledge_graph/knowledge_detail_screen.dart'
    as _i3;
import 'package:suoke_life/presentation/screens/knowledge_graph/knowledge_graph_screen.dart'
    as _i4;
import 'package:suoke_life/presentation/screens/life/life_screen.dart' as _i5;
import 'package:suoke_life/presentation/screens/profile/profile_screen.dart'
    as _i8;
import 'package:suoke_life/presentation/screens/suoke/suoke_screen.dart'
    as _i10;
import 'package:suoke_life/presentation/screens/welcome/welcome_screen.dart'
    as _i11;

abstract class $AppRouter extends _i12.RootStackRouter {
  $AppRouter({super.navigatorKey});

  @override
  final Map<String, _i12.PageFactory> pagesMap = {
    ExploreRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i1.ExploreScreen(),
      );
    },
    HomeRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i2.HomeScreen(),
      );
    },
    KnowledgeDetailRoute.name: (routeData) {
      final args = routeData.argsAs<KnowledgeDetailRouteArgs>();
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: _i3.KnowledgeDetailScreen(
          key: args.key,
          nodeId: args.nodeId,
          nodeType: args.nodeType,
          nodeDescription: args.nodeDescription,
        ),
      );
    },
    KnowledgeGraphRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i4.KnowledgeGraphScreen(),
      );
    },
    LifeRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i5.LifeScreen(),
      );
    },
    LoginRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i6.LoginScreen(),
      );
    },
    MainWrapperRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i7.MainWrapperScreen(),
      );
    },
    ProfileRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i8.ProfileScreen(),
      );
    },
    RAGDemoRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i9.RAGDemoScreen(),
      );
    },
    SuokeRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i10.SuokeScreen(),
      );
    },
    WelcomeRoute.name: (routeData) {
      return _i12.AutoRoutePage<dynamic>(
        routeData: routeData,
        child: const _i11.WelcomeScreen(),
      );
    },
  };
}

/// generated route for
/// [_i1.ExploreScreen]
class ExploreRoute extends _i12.PageRouteInfo<void> {
  const ExploreRoute({List<_i12.PageRouteInfo>? children})
      : super(
          ExploreRoute.name,
          initialChildren: children,
        );

  static const String name = 'ExploreRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}

/// generated route for
/// [_i2.HomeScreen]
class HomeRoute extends _i12.PageRouteInfo<void> {
  const HomeRoute({List<_i12.PageRouteInfo>? children})
      : super(
          HomeRoute.name,
          initialChildren: children,
        );

  static const String name = 'HomeRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}

/// generated route for
/// [_i3.KnowledgeDetailScreen]
class KnowledgeDetailRoute
    extends _i12.PageRouteInfo<KnowledgeDetailRouteArgs> {
  KnowledgeDetailRoute({
    _i13.Key? key,
    required String nodeId,
    required String nodeType,
    required String nodeDescription,
    List<_i12.PageRouteInfo>? children,
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

  static const _i12.PageInfo<KnowledgeDetailRouteArgs> page =
      _i12.PageInfo<KnowledgeDetailRouteArgs>(name);
}

class KnowledgeDetailRouteArgs {
  const KnowledgeDetailRouteArgs({
    this.key,
    required this.nodeId,
    required this.nodeType,
    required this.nodeDescription,
  });

  final _i13.Key? key;

  final String nodeId;

  final String nodeType;

  final String nodeDescription;

  @override
  String toString() {
    return 'KnowledgeDetailRouteArgs{key: $key, nodeId: $nodeId, nodeType: $nodeType, nodeDescription: $nodeDescription}';
  }
}

/// generated route for
/// [_i4.KnowledgeGraphScreen]
class KnowledgeGraphRoute extends _i12.PageRouteInfo<void> {
  const KnowledgeGraphRoute({List<_i12.PageRouteInfo>? children})
      : super(
          KnowledgeGraphRoute.name,
          initialChildren: children,
        );

  static const String name = 'KnowledgeGraphRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}

/// generated route for
/// [_i5.LifeScreen]
class LifeRoute extends _i12.PageRouteInfo<void> {
  const LifeRoute({List<_i12.PageRouteInfo>? children})
      : super(
          LifeRoute.name,
          initialChildren: children,
        );

  static const String name = 'LifeRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}

/// generated route for
/// [_i6.LoginScreen]
class LoginRoute extends _i12.PageRouteInfo<void> {
  const LoginRoute({List<_i12.PageRouteInfo>? children})
      : super(
          LoginRoute.name,
          initialChildren: children,
        );

  static const String name = 'LoginRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}

/// generated route for
/// [_i7.MainWrapperScreen]
class MainWrapperRoute extends _i12.PageRouteInfo<void> {
  const MainWrapperRoute({List<_i12.PageRouteInfo>? children})
      : super(
          MainWrapperRoute.name,
          initialChildren: children,
        );

  static const String name = 'MainWrapperRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}

/// generated route for
/// [_i8.ProfileScreen]
class ProfileRoute extends _i12.PageRouteInfo<void> {
  const ProfileRoute({List<_i12.PageRouteInfo>? children})
      : super(
          ProfileRoute.name,
          initialChildren: children,
        );

  static const String name = 'ProfileRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}

/// generated route for
/// [_i9.RAGDemoScreen]
class RAGDemoRoute extends _i12.PageRouteInfo<void> {
  const RAGDemoRoute({List<_i12.PageRouteInfo>? children})
      : super(
          RAGDemoRoute.name,
          initialChildren: children,
        );

  static const String name = 'RAGDemoRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}

/// generated route for
/// [_i10.SuokeScreen]
class SuokeRoute extends _i12.PageRouteInfo<void> {
  const SuokeRoute({List<_i12.PageRouteInfo>? children})
      : super(
          SuokeRoute.name,
          initialChildren: children,
        );

  static const String name = 'SuokeRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}

/// generated route for
/// [_i11.WelcomeScreen]
class WelcomeRoute extends _i12.PageRouteInfo<void> {
  const WelcomeRoute({List<_i12.PageRouteInfo>? children})
      : super(
          WelcomeRoute.name,
          initialChildren: children,
        );

  static const String name = 'WelcomeRoute';

  static const _i12.PageInfo<void> page = _i12.PageInfo<void>(name);
}
