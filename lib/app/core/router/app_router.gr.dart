// dart format width=80
// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// AutoRouterGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:auto_route/auto_route.dart' as _i38;
import 'package:flutter/material.dart' as _i39;
import 'package:suoke_life_app/app/features/home/pages/home_page.dart' as _i18;
import 'package:suoke_life_app/app/features/profile/pages/profile_page.dart'
    as _i26;
import 'package:suoke_life_app/app/features/suoke/pages/suoke_page.dart'
    as _i34;
import 'package:suoke_life_app/app/presentation/pages/about/about_page.dart'
    as _i1;
import 'package:suoke_life_app/app/presentation/pages/admin/admin_panel_page.dart'
    as _i2;
import 'package:suoke_life_app/app/presentation/pages/auth/login_page.dart'
    as _i22;
import 'package:suoke_life_app/app/presentation/pages/auth/register_page.dart'
    as _i30;
import 'package:suoke_life_app/app/presentation/pages/base/base_page.dart'
    as _i3;
import 'package:suoke_life_app/app/presentation/pages/chat/chat_detail_page.dart'
    as _i5;
import 'package:suoke_life_app/app/presentation/pages/chat/chat_page.dart'
    as _i6;
import 'package:suoke_life_app/app/presentation/pages/coffee/coffee_page.dart'
    as _i7;
import 'package:suoke_life_app/app/presentation/pages/explore/explore_page.dart'
    as _i9;
import 'package:suoke_life_app/app/presentation/pages/explore/explore_search_page.dart'
    as _i10;
import 'package:suoke_life_app/app/presentation/pages/explore/knowledge_graph_page.dart'
    as _i19;
import 'package:suoke_life_app/app/presentation/pages/favorites/favorites_page.dart'
    as _i11;
import 'package:suoke_life_app/app/presentation/pages/health/health_advice_page.dart'
    as _i14;
import 'package:suoke_life_app/app/presentation/pages/help/feedback_page.dart'
    as _i12;
import 'package:suoke_life_app/app/presentation/pages/help/help_page.dart'
    as _i16;
import 'package:suoke_life_app/app/presentation/pages/legal/licenses_page.dart'
    as _i20;
import 'package:suoke_life_app/app/presentation/pages/legal/privacy_policy_page.dart'
    as _i25;
import 'package:suoke_life_app/app/presentation/pages/legal/user_agreement_page.dart'
    as _i37;
import 'package:suoke_life_app/app/presentation/pages/life/calendar_page.dart'
    as _i4;
import 'package:suoke_life_app/app/presentation/pages/life/health_advice_detail_page.dart'
    as _i13;
import 'package:suoke_life_app/app/presentation/pages/life/health_stats_page.dart'
    as _i15;
import 'package:suoke_life_app/app/presentation/pages/life/life_page.dart'
    as _i21;
import 'package:suoke_life_app/app/presentation/pages/life/record_detail_page.dart'
    as _i28;
import 'package:suoke_life_app/app/presentation/pages/main/main_page.dart'
    as _i24;
import 'package:suoke_life_app/app/presentation/pages/main_navigation_page.dart'
    as _i23;
import 'package:suoke_life_app/app/presentation/pages/profile/device_management_page.dart'
    as _i8;
import 'package:suoke_life_app/app/presentation/pages/profile/history_page.dart'
    as _i17;
import 'package:suoke_life_app/app/presentation/pages/record/record_edit_page.dart'
    as _i29;
import 'package:suoke_life_app/app/presentation/pages/service/service_detail_page.dart'
    as _i31;
import 'package:suoke_life_app/app/presentation/pages/service/service_list_page.dart'
    as _i32;
import 'package:suoke_life_app/app/presentation/pages/settings/settings_page.dart'
    as _i33;
import 'package:suoke_life_app/app/presentation/pages/suoke/questionnaire_list_page.dart'
    as _i27;
import 'package:suoke_life_app/app/presentation/pages/suoke/tcm_test_page.dart'
    as _i35;
import 'package:suoke_life_app/app/presentation/pages/topic/topic_detail_page.dart'
    as _i36;

/// generated route for
/// [_i1.AboutPage]
class AboutRoute extends _i38.PageRouteInfo<void> {
  const AboutRoute({List<_i38.PageRouteInfo>? children})
    : super(AboutRoute.name, initialChildren: children);

  static const String name = 'AboutRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i1.AboutPage();
    },
  );
}

/// generated route for
/// [_i2.AdminPanelPage]
class AdminPanelRoute extends _i38.PageRouteInfo<void> {
  const AdminPanelRoute({List<_i38.PageRouteInfo>? children})
    : super(AdminPanelRoute.name, initialChildren: children);

  static const String name = 'AdminPanelRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i2.AdminPanelPage();
    },
  );
}

/// generated route for
/// [_i3.BasePage]
class BaseRoute extends _i38.PageRouteInfo<BaseRouteArgs> {
  BaseRoute({
    _i39.Key? key,
    required String title,
    required _i39.Widget body,
    List<_i39.Widget>? actions,
    _i39.Widget? floatingActionButton,
    _i39.Widget? bottomNavigationBar,
    List<_i38.PageRouteInfo>? children,
  }) : super(
         BaseRoute.name,
         args: BaseRouteArgs(
           key: key,
           title: title,
           body: body,
           actions: actions,
           floatingActionButton: floatingActionButton,
           bottomNavigationBar: bottomNavigationBar,
         ),
         initialChildren: children,
       );

  static const String name = 'BaseRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<BaseRouteArgs>();
      return _i3.BasePage(
        key: args.key,
        title: args.title,
        body: args.body,
        actions: args.actions,
        floatingActionButton: args.floatingActionButton,
        bottomNavigationBar: args.bottomNavigationBar,
      );
    },
  );
}

class BaseRouteArgs {
  const BaseRouteArgs({
    this.key,
    required this.title,
    required this.body,
    this.actions,
    this.floatingActionButton,
    this.bottomNavigationBar,
  });

  final _i39.Key? key;

  final String title;

  final _i39.Widget body;

  final List<_i39.Widget>? actions;

  final _i39.Widget? floatingActionButton;

  final _i39.Widget? bottomNavigationBar;

  @override
  String toString() {
    return 'BaseRouteArgs{key: $key, title: $title, body: $body, actions: $actions, floatingActionButton: $floatingActionButton, bottomNavigationBar: $bottomNavigationBar}';
  }
}

/// generated route for
/// [_i4.CalendarPage]
class CalendarRoute extends _i38.PageRouteInfo<void> {
  const CalendarRoute({List<_i38.PageRouteInfo>? children})
    : super(CalendarRoute.name, initialChildren: children);

  static const String name = 'CalendarRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i4.CalendarPage();
    },
  );
}

/// generated route for
/// [_i5.ChatDetailPage]
class ChatDetailRoute extends _i38.PageRouteInfo<ChatDetailRouteArgs> {
  ChatDetailRoute({
    _i39.Key? key,
    required String chatId,
    List<_i38.PageRouteInfo>? children,
  }) : super(
         ChatDetailRoute.name,
         args: ChatDetailRouteArgs(key: key, chatId: chatId),
         rawPathParams: {'id': chatId},
         initialChildren: children,
       );

  static const String name = 'ChatDetailRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<ChatDetailRouteArgs>(
        orElse: () => ChatDetailRouteArgs(chatId: pathParams.getString('id')),
      );
      return _i5.ChatDetailPage(key: args.key, chatId: args.chatId);
    },
  );
}

class ChatDetailRouteArgs {
  const ChatDetailRouteArgs({this.key, required this.chatId});

  final _i39.Key? key;

  final String chatId;

  @override
  String toString() {
    return 'ChatDetailRouteArgs{key: $key, chatId: $chatId}';
  }
}

/// generated route for
/// [_i6.ChatPage]
class ChatRoute extends _i38.PageRouteInfo<ChatRouteArgs> {
  ChatRoute({
    _i39.Key? key,
    required String assistantId,
    List<_i38.PageRouteInfo>? children,
  }) : super(
         ChatRoute.name,
         args: ChatRouteArgs(key: key, assistantId: assistantId),
         rawPathParams: {'assistantId': assistantId},
         initialChildren: children,
       );

  static const String name = 'ChatRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<ChatRouteArgs>(
        orElse:
            () =>
                ChatRouteArgs(assistantId: pathParams.getString('assistantId')),
      );
      return _i6.ChatPage(key: args.key, assistantId: args.assistantId);
    },
  );
}

class ChatRouteArgs {
  const ChatRouteArgs({this.key, required this.assistantId});

  final _i39.Key? key;

  final String assistantId;

  @override
  String toString() {
    return 'ChatRouteArgs{key: $key, assistantId: $assistantId}';
  }
}

/// generated route for
/// [_i7.CoffeePage]
class CoffeeRoute extends _i38.PageRouteInfo<void> {
  const CoffeeRoute({List<_i38.PageRouteInfo>? children})
    : super(CoffeeRoute.name, initialChildren: children);

  static const String name = 'CoffeeRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i7.CoffeePage();
    },
  );
}

/// generated route for
/// [_i8.DeviceManagementPage]
class DeviceManagementRoute extends _i38.PageRouteInfo<void> {
  const DeviceManagementRoute({List<_i38.PageRouteInfo>? children})
    : super(DeviceManagementRoute.name, initialChildren: children);

  static const String name = 'DeviceManagementRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i8.DeviceManagementPage();
    },
  );
}

/// generated route for
/// [_i9.ExplorePage]
class ExploreRoute extends _i38.PageRouteInfo<void> {
  const ExploreRoute({List<_i38.PageRouteInfo>? children})
    : super(ExploreRoute.name, initialChildren: children);

  static const String name = 'ExploreRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i9.ExplorePage();
    },
  );
}

/// generated route for
/// [_i10.ExploreSearchPage]
class ExploreSearchRoute extends _i38.PageRouteInfo<void> {
  const ExploreSearchRoute({List<_i38.PageRouteInfo>? children})
    : super(ExploreSearchRoute.name, initialChildren: children);

  static const String name = 'ExploreSearchRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i10.ExploreSearchPage();
    },
  );
}

/// generated route for
/// [_i11.FavoritesPage]
class FavoritesRoute extends _i38.PageRouteInfo<void> {
  const FavoritesRoute({List<_i38.PageRouteInfo>? children})
    : super(FavoritesRoute.name, initialChildren: children);

  static const String name = 'FavoritesRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i11.FavoritesPage();
    },
  );
}

/// generated route for
/// [_i12.FeedbackPage]
class FeedbackRoute extends _i38.PageRouteInfo<void> {
  const FeedbackRoute({List<_i38.PageRouteInfo>? children})
    : super(FeedbackRoute.name, initialChildren: children);

  static const String name = 'FeedbackRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i12.FeedbackPage();
    },
  );
}

/// generated route for
/// [_i13.HealthAdviceDetailPage]
class HealthAdviceDetailRoute
    extends _i38.PageRouteInfo<HealthAdviceDetailRouteArgs> {
  HealthAdviceDetailRoute({
    required String id,
    _i39.Key? key,
    List<_i38.PageRouteInfo>? children,
  }) : super(
         HealthAdviceDetailRoute.name,
         args: HealthAdviceDetailRouteArgs(id: id, key: key),
         rawPathParams: {'id': id},
         initialChildren: children,
       );

  static const String name = 'HealthAdviceDetailRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<HealthAdviceDetailRouteArgs>(
        orElse:
            () => HealthAdviceDetailRouteArgs(id: pathParams.getString('id')),
      );
      return _i13.HealthAdviceDetailPage(id: args.id, key: args.key);
    },
  );
}

class HealthAdviceDetailRouteArgs {
  const HealthAdviceDetailRouteArgs({required this.id, this.key});

  final String id;

  final _i39.Key? key;

  @override
  String toString() {
    return 'HealthAdviceDetailRouteArgs{id: $id, key: $key}';
  }
}

/// generated route for
/// [_i14.HealthAdvicePage]
class HealthAdviceRoute extends _i38.PageRouteInfo<void> {
  const HealthAdviceRoute({List<_i38.PageRouteInfo>? children})
    : super(HealthAdviceRoute.name, initialChildren: children);

  static const String name = 'HealthAdviceRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i14.HealthAdvicePage();
    },
  );
}

/// generated route for
/// [_i15.HealthStatsPage]
class HealthStatsRoute extends _i38.PageRouteInfo<void> {
  const HealthStatsRoute({List<_i38.PageRouteInfo>? children})
    : super(HealthStatsRoute.name, initialChildren: children);

  static const String name = 'HealthStatsRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i15.HealthStatsPage();
    },
  );
}

/// generated route for
/// [_i16.HelpPage]
class HelpRoute extends _i38.PageRouteInfo<void> {
  const HelpRoute({List<_i38.PageRouteInfo>? children})
    : super(HelpRoute.name, initialChildren: children);

  static const String name = 'HelpRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i16.HelpPage();
    },
  );
}

/// generated route for
/// [_i17.HistoryPage]
class HistoryRoute extends _i38.PageRouteInfo<void> {
  const HistoryRoute({List<_i38.PageRouteInfo>? children})
    : super(HistoryRoute.name, initialChildren: children);

  static const String name = 'HistoryRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i17.HistoryPage();
    },
  );
}

/// generated route for
/// [_i18.HomePage]
class HomeRoute extends _i38.PageRouteInfo<void> {
  const HomeRoute({List<_i38.PageRouteInfo>? children})
    : super(HomeRoute.name, initialChildren: children);

  static const String name = 'HomeRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i18.HomePage();
    },
  );
}

/// generated route for
/// [_i19.KnowledgeGraphPage]
class KnowledgeGraphRoute extends _i38.PageRouteInfo<void> {
  const KnowledgeGraphRoute({List<_i38.PageRouteInfo>? children})
    : super(KnowledgeGraphRoute.name, initialChildren: children);

  static const String name = 'KnowledgeGraphRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i19.KnowledgeGraphPage();
    },
  );
}

/// generated route for
/// [_i20.LicensesPage]
class LicensesRoute extends _i38.PageRouteInfo<void> {
  const LicensesRoute({List<_i38.PageRouteInfo>? children})
    : super(LicensesRoute.name, initialChildren: children);

  static const String name = 'LicensesRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i20.LicensesPage();
    },
  );
}

/// generated route for
/// [_i21.LifePage]
class LifeRoute extends _i38.PageRouteInfo<void> {
  const LifeRoute({List<_i38.PageRouteInfo>? children})
    : super(LifeRoute.name, initialChildren: children);

  static const String name = 'LifeRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i21.LifePage();
    },
  );
}

/// generated route for
/// [_i22.LoginPage]
class LoginRoute extends _i38.PageRouteInfo<void> {
  const LoginRoute({List<_i38.PageRouteInfo>? children})
    : super(LoginRoute.name, initialChildren: children);

  static const String name = 'LoginRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i22.LoginPage();
    },
  );
}

/// generated route for
/// [_i23.MainNavigationPage]
class MainNavigationRoute extends _i38.PageRouteInfo<void> {
  const MainNavigationRoute({List<_i38.PageRouteInfo>? children})
    : super(MainNavigationRoute.name, initialChildren: children);

  static const String name = 'MainNavigationRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i23.MainNavigationPage();
    },
  );
}

/// generated route for
/// [_i24.MainPage]
class MainRoute extends _i38.PageRouteInfo<void> {
  const MainRoute({List<_i38.PageRouteInfo>? children})
    : super(MainRoute.name, initialChildren: children);

  static const String name = 'MainRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i24.MainPage();
    },
  );
}

/// generated route for
/// [_i25.PrivacyPolicyPage]
class PrivacyPolicyRoute extends _i38.PageRouteInfo<void> {
  const PrivacyPolicyRoute({List<_i38.PageRouteInfo>? children})
    : super(PrivacyPolicyRoute.name, initialChildren: children);

  static const String name = 'PrivacyPolicyRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i25.PrivacyPolicyPage();
    },
  );
}

/// generated route for
/// [_i26.ProfilePage]
class ProfileRoute extends _i38.PageRouteInfo<void> {
  const ProfileRoute({List<_i38.PageRouteInfo>? children})
    : super(ProfileRoute.name, initialChildren: children);

  static const String name = 'ProfileRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i26.ProfilePage();
    },
  );
}

/// generated route for
/// [_i27.QuestionnaireListPage]
class QuestionnaireListRoute extends _i38.PageRouteInfo<void> {
  const QuestionnaireListRoute({List<_i38.PageRouteInfo>? children})
    : super(QuestionnaireListRoute.name, initialChildren: children);

  static const String name = 'QuestionnaireListRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i27.QuestionnaireListPage();
    },
  );
}

/// generated route for
/// [_i28.RecordDetailPage]
class RecordDetailRoute extends _i38.PageRouteInfo<RecordDetailRouteArgs> {
  RecordDetailRoute({
    required String id,
    _i39.Key? key,
    List<_i38.PageRouteInfo>? children,
  }) : super(
         RecordDetailRoute.name,
         args: RecordDetailRouteArgs(id: id, key: key),
         rawPathParams: {'id': id},
         initialChildren: children,
       );

  static const String name = 'RecordDetailRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<RecordDetailRouteArgs>(
        orElse: () => RecordDetailRouteArgs(id: pathParams.getString('id')),
      );
      return _i28.RecordDetailPage(id: args.id, key: args.key);
    },
  );
}

class RecordDetailRouteArgs {
  const RecordDetailRouteArgs({required this.id, this.key});

  final String id;

  final _i39.Key? key;

  @override
  String toString() {
    return 'RecordDetailRouteArgs{id: $id, key: $key}';
  }
}

/// generated route for
/// [_i29.RecordEditPage]
class RecordEditRoute extends _i38.PageRouteInfo<RecordEditRouteArgs> {
  RecordEditRoute({
    _i39.Key? key,
    String? id,
    List<_i38.PageRouteInfo>? children,
  }) : super(
         RecordEditRoute.name,
         args: RecordEditRouteArgs(key: key, id: id),
         rawPathParams: {'id': id},
         initialChildren: children,
       );

  static const String name = 'RecordEditRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<RecordEditRouteArgs>(
        orElse: () => RecordEditRouteArgs(id: pathParams.optString('id')),
      );
      return _i29.RecordEditPage(key: args.key, id: args.id);
    },
  );
}

class RecordEditRouteArgs {
  const RecordEditRouteArgs({this.key, this.id});

  final _i39.Key? key;

  final String? id;

  @override
  String toString() {
    return 'RecordEditRouteArgs{key: $key, id: $id}';
  }
}

/// generated route for
/// [_i30.RegisterPage]
class RegisterRoute extends _i38.PageRouteInfo<void> {
  const RegisterRoute({List<_i38.PageRouteInfo>? children})
    : super(RegisterRoute.name, initialChildren: children);

  static const String name = 'RegisterRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i30.RegisterPage();
    },
  );
}

/// generated route for
/// [_i31.ServiceDetailPage]
class ServiceDetailRoute extends _i38.PageRouteInfo<ServiceDetailRouteArgs> {
  ServiceDetailRoute({
    _i39.Key? key,
    required String id,
    List<_i38.PageRouteInfo>? children,
  }) : super(
         ServiceDetailRoute.name,
         args: ServiceDetailRouteArgs(key: key, id: id),
         rawPathParams: {'id': id},
         initialChildren: children,
       );

  static const String name = 'ServiceDetailRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<ServiceDetailRouteArgs>(
        orElse: () => ServiceDetailRouteArgs(id: pathParams.getString('id')),
      );
      return _i31.ServiceDetailPage(key: args.key, id: args.id);
    },
  );
}

class ServiceDetailRouteArgs {
  const ServiceDetailRouteArgs({this.key, required this.id});

  final _i39.Key? key;

  final String id;

  @override
  String toString() {
    return 'ServiceDetailRouteArgs{key: $key, id: $id}';
  }
}

/// generated route for
/// [_i32.ServiceListPage]
class ServiceListRoute extends _i38.PageRouteInfo<ServiceListRouteArgs> {
  ServiceListRoute({
    _i39.Key? key,
    required String categoryId,
    List<_i38.PageRouteInfo>? children,
  }) : super(
         ServiceListRoute.name,
         args: ServiceListRouteArgs(key: key, categoryId: categoryId),
         rawPathParams: {'categoryId': categoryId},
         initialChildren: children,
       );

  static const String name = 'ServiceListRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<ServiceListRouteArgs>(
        orElse:
            () => ServiceListRouteArgs(
              categoryId: pathParams.getString('categoryId'),
            ),
      );
      return _i32.ServiceListPage(key: args.key, categoryId: args.categoryId);
    },
  );
}

class ServiceListRouteArgs {
  const ServiceListRouteArgs({this.key, required this.categoryId});

  final _i39.Key? key;

  final String categoryId;

  @override
  String toString() {
    return 'ServiceListRouteArgs{key: $key, categoryId: $categoryId}';
  }
}

/// generated route for
/// [_i33.SettingsPage]
class SettingsRoute extends _i38.PageRouteInfo<void> {
  const SettingsRoute({List<_i38.PageRouteInfo>? children})
    : super(SettingsRoute.name, initialChildren: children);

  static const String name = 'SettingsRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i33.SettingsPage();
    },
  );
}

/// generated route for
/// [_i34.SuokePage]
class SuokeRoute extends _i38.PageRouteInfo<void> {
  const SuokeRoute({List<_i38.PageRouteInfo>? children})
    : super(SuokeRoute.name, initialChildren: children);

  static const String name = 'SuokeRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i34.SuokePage();
    },
  );
}

/// generated route for
/// [_i35.TCMTestPage]
class TCMTestRoute extends _i38.PageRouteInfo<void> {
  const TCMTestRoute({List<_i38.PageRouteInfo>? children})
    : super(TCMTestRoute.name, initialChildren: children);

  static const String name = 'TCMTestRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i35.TCMTestPage();
    },
  );
}

/// generated route for
/// [_i36.TopicDetailPage]
class TopicDetailRoute extends _i38.PageRouteInfo<TopicDetailRouteArgs> {
  TopicDetailRoute({
    _i39.Key? key,
    required String id,
    List<_i38.PageRouteInfo>? children,
  }) : super(
         TopicDetailRoute.name,
         args: TopicDetailRouteArgs(key: key, id: id),
         rawPathParams: {'id': id},
         initialChildren: children,
       );

  static const String name = 'TopicDetailRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<TopicDetailRouteArgs>(
        orElse: () => TopicDetailRouteArgs(id: pathParams.getString('id')),
      );
      return _i36.TopicDetailPage(key: args.key, id: args.id);
    },
  );
}

class TopicDetailRouteArgs {
  const TopicDetailRouteArgs({this.key, required this.id});

  final _i39.Key? key;

  final String id;

  @override
  String toString() {
    return 'TopicDetailRouteArgs{key: $key, id: $id}';
  }
}

/// generated route for
/// [_i37.UserAgreementPage]
class UserAgreementRoute extends _i38.PageRouteInfo<void> {
  const UserAgreementRoute({List<_i38.PageRouteInfo>? children})
    : super(UserAgreementRoute.name, initialChildren: children);

  static const String name = 'UserAgreementRoute';

  static _i38.PageInfo page = _i38.PageInfo(
    name,
    builder: (data) {
      return const _i37.UserAgreementPage();
    },
  );
}
