// dart format width=80
// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// AutoRouterGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

part of 'app_router.dart';

/// generated route for
/// [AboutPage]
class AboutRoute extends PageRouteInfo<void> {
  const AboutRoute({List<PageRouteInfo>? children})
    : super(AboutRoute.name, initialChildren: children);

  static const String name = 'AboutRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const AboutPage();
    },
  );
}

/// generated route for
/// [AdminPanelPage]
class AdminPanelRoute extends PageRouteInfo<void> {
  const AdminPanelRoute({List<PageRouteInfo>? children})
    : super(AdminPanelRoute.name, initialChildren: children);

  static const String name = 'AdminPanelRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const AdminPanelPage();
    },
  );
}

/// generated route for
/// [BasePage]
class BaseRoute extends PageRouteInfo<BaseRouteArgs> {
  BaseRoute({
    Key? key,
    required String title,
    required Widget body,
    List<Widget>? actions,
    Widget? floatingActionButton,
    Widget? bottomNavigationBar,
    List<PageRouteInfo>? children,
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

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<BaseRouteArgs>();
      return BasePage(
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

  final Key? key;

  final String title;

  final Widget body;

  final List<Widget>? actions;

  final Widget? floatingActionButton;

  final Widget? bottomNavigationBar;

  @override
  String toString() {
    return 'BaseRouteArgs{key: $key, title: $title, body: $body, actions: $actions, floatingActionButton: $floatingActionButton, bottomNavigationBar: $bottomNavigationBar}';
  }
}

/// generated route for
/// [CalendarPage]
class CalendarRoute extends PageRouteInfo<void> {
  const CalendarRoute({List<PageRouteInfo>? children})
    : super(CalendarRoute.name, initialChildren: children);

  static const String name = 'CalendarRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const CalendarPage();
    },
  );
}

/// generated route for
/// [ChatDetailPage]
class ChatDetailRoute extends PageRouteInfo<ChatDetailRouteArgs> {
  ChatDetailRoute({
    Key? key,
    required String chatId,
    List<PageRouteInfo>? children,
  }) : super(
         ChatDetailRoute.name,
         args: ChatDetailRouteArgs(key: key, chatId: chatId),
         rawPathParams: {'id': chatId},
         initialChildren: children,
       );

  static const String name = 'ChatDetailRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<ChatDetailRouteArgs>(
        orElse: () => ChatDetailRouteArgs(chatId: pathParams.getString('id')),
      );
      return ChatDetailPage(key: args.key, chatId: args.chatId);
    },
  );
}

class ChatDetailRouteArgs {
  const ChatDetailRouteArgs({this.key, required this.chatId});

  final Key? key;

  final String chatId;

  @override
  String toString() {
    return 'ChatDetailRouteArgs{key: $key, chatId: $chatId}';
  }
}

/// generated route for
/// [ChatPage]
class ChatRoute extends PageRouteInfo<ChatRouteArgs> {
  ChatRoute({
    Key? key,
    required String assistantId,
    List<PageRouteInfo>? children,
  }) : super(
         ChatRoute.name,
         args: ChatRouteArgs(key: key, assistantId: assistantId),
         rawPathParams: {'assistantId': assistantId},
         initialChildren: children,
       );

  static const String name = 'ChatRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<ChatRouteArgs>(
        orElse:
            () =>
                ChatRouteArgs(assistantId: pathParams.getString('assistantId')),
      );
      return ChatPage(key: args.key, assistantId: args.assistantId);
    },
  );
}

class ChatRouteArgs {
  const ChatRouteArgs({this.key, required this.assistantId});

  final Key? key;

  final String assistantId;

  @override
  String toString() {
    return 'ChatRouteArgs{key: $key, assistantId: $assistantId}';
  }
}

/// generated route for
/// [CoffeePage]
class CoffeeRoute extends PageRouteInfo<void> {
  const CoffeeRoute({List<PageRouteInfo>? children})
    : super(CoffeeRoute.name, initialChildren: children);

  static const String name = 'CoffeeRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const CoffeePage();
    },
  );
}

/// generated route for
/// [DeviceManagementPage]
class DeviceManagementRoute extends PageRouteInfo<void> {
  const DeviceManagementRoute({List<PageRouteInfo>? children})
    : super(DeviceManagementRoute.name, initialChildren: children);

  static const String name = 'DeviceManagementRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const DeviceManagementPage();
    },
  );
}

/// generated route for
/// [ExplorePage]
class ExploreRoute extends PageRouteInfo<void> {
  const ExploreRoute({List<PageRouteInfo>? children})
    : super(ExploreRoute.name, initialChildren: children);

  static const String name = 'ExploreRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const ExplorePage();
    },
  );
}

/// generated route for
/// [ExploreSearchPage]
class ExploreSearchRoute extends PageRouteInfo<void> {
  const ExploreSearchRoute({List<PageRouteInfo>? children})
    : super(ExploreSearchRoute.name, initialChildren: children);

  static const String name = 'ExploreSearchRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const ExploreSearchPage();
    },
  );
}

/// generated route for
/// [FavoritesPage]
class FavoritesRoute extends PageRouteInfo<void> {
  const FavoritesRoute({List<PageRouteInfo>? children})
    : super(FavoritesRoute.name, initialChildren: children);

  static const String name = 'FavoritesRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const FavoritesPage();
    },
  );
}

/// generated route for
/// [FeedbackPage]
class FeedbackRoute extends PageRouteInfo<void> {
  const FeedbackRoute({List<PageRouteInfo>? children})
    : super(FeedbackRoute.name, initialChildren: children);

  static const String name = 'FeedbackRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const FeedbackPage();
    },
  );
}

/// generated route for
/// [HealthAdviceDetailPage]
class HealthAdviceDetailRoute
    extends PageRouteInfo<HealthAdviceDetailRouteArgs> {
  HealthAdviceDetailRoute({
    required String id,
    Key? key,
    List<PageRouteInfo>? children,
  }) : super(
         HealthAdviceDetailRoute.name,
         args: HealthAdviceDetailRouteArgs(id: id, key: key),
         rawPathParams: {'id': id},
         initialChildren: children,
       );

  static const String name = 'HealthAdviceDetailRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<HealthAdviceDetailRouteArgs>(
        orElse:
            () => HealthAdviceDetailRouteArgs(id: pathParams.getString('id')),
      );
      return HealthAdviceDetailPage(id: args.id, key: args.key);
    },
  );
}

class HealthAdviceDetailRouteArgs {
  const HealthAdviceDetailRouteArgs({required this.id, this.key});

  final String id;

  final Key? key;

  @override
  String toString() {
    return 'HealthAdviceDetailRouteArgs{id: $id, key: $key}';
  }
}

/// generated route for
/// [HealthAdvicePage]
class HealthAdviceRoute extends PageRouteInfo<void> {
  const HealthAdviceRoute({List<PageRouteInfo>? children})
    : super(HealthAdviceRoute.name, initialChildren: children);

  static const String name = 'HealthAdviceRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const HealthAdvicePage();
    },
  );
}

/// generated route for
/// [HealthStatsPage]
class HealthStatsRoute extends PageRouteInfo<void> {
  const HealthStatsRoute({List<PageRouteInfo>? children})
    : super(HealthStatsRoute.name, initialChildren: children);

  static const String name = 'HealthStatsRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const HealthStatsPage();
    },
  );
}

/// generated route for
/// [HelpPage]
class HelpRoute extends PageRouteInfo<void> {
  const HelpRoute({List<PageRouteInfo>? children})
    : super(HelpRoute.name, initialChildren: children);

  static const String name = 'HelpRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const HelpPage();
    },
  );
}

/// generated route for
/// [HistoryPage]
class HistoryRoute extends PageRouteInfo<void> {
  const HistoryRoute({List<PageRouteInfo>? children})
    : super(HistoryRoute.name, initialChildren: children);

  static const String name = 'HistoryRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const HistoryPage();
    },
  );
}

/// generated route for
/// [HomePage]
class HomeRoute extends PageRouteInfo<void> {
  const HomeRoute({List<PageRouteInfo>? children})
    : super(HomeRoute.name, initialChildren: children);

  static const String name = 'HomeRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const HomePage();
    },
  );
}

/// generated route for
/// [KnowledgeGraphPage]
class KnowledgeGraphRoute extends PageRouteInfo<void> {
  const KnowledgeGraphRoute({List<PageRouteInfo>? children})
    : super(KnowledgeGraphRoute.name, initialChildren: children);

  static const String name = 'KnowledgeGraphRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const KnowledgeGraphPage();
    },
  );
}

/// generated route for
/// [LicensesPage]
class LicensesRoute extends PageRouteInfo<void> {
  const LicensesRoute({List<PageRouteInfo>? children})
    : super(LicensesRoute.name, initialChildren: children);

  static const String name = 'LicensesRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const LicensesPage();
    },
  );
}

/// generated route for
/// [LifePage]
class LifeRoute extends PageRouteInfo<void> {
  const LifeRoute({List<PageRouteInfo>? children})
    : super(LifeRoute.name, initialChildren: children);

  static const String name = 'LifeRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const LifePage();
    },
  );
}

/// generated route for
/// [LoginPage]
class LoginRoute extends PageRouteInfo<void> {
  const LoginRoute({List<PageRouteInfo>? children})
    : super(LoginRoute.name, initialChildren: children);

  static const String name = 'LoginRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const LoginPage();
    },
  );
}

/// generated route for
/// [MainNavigationPage]
class MainNavigationRoute extends PageRouteInfo<void> {
  const MainNavigationRoute({List<PageRouteInfo>? children})
    : super(MainNavigationRoute.name, initialChildren: children);

  static const String name = 'MainNavigationRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const MainNavigationPage();
    },
  );
}

/// generated route for
/// [MainPage]
class MainRoute extends PageRouteInfo<void> {
  const MainRoute({List<PageRouteInfo>? children})
    : super(MainRoute.name, initialChildren: children);

  static const String name = 'MainRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const MainPage();
    },
  );
}

/// generated route for
/// [PrivacyPolicyPage]
class PrivacyPolicyRoute extends PageRouteInfo<void> {
  const PrivacyPolicyRoute({List<PageRouteInfo>? children})
    : super(PrivacyPolicyRoute.name, initialChildren: children);

  static const String name = 'PrivacyPolicyRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const PrivacyPolicyPage();
    },
  );
}

/// generated route for
/// [ProfilePage]
class ProfileRoute extends PageRouteInfo<void> {
  const ProfileRoute({List<PageRouteInfo>? children})
    : super(ProfileRoute.name, initialChildren: children);

  static const String name = 'ProfileRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const ProfilePage();
    },
  );
}

/// generated route for
/// [QuestionnaireListPage]
class QuestionnaireListRoute extends PageRouteInfo<void> {
  const QuestionnaireListRoute({List<PageRouteInfo>? children})
    : super(QuestionnaireListRoute.name, initialChildren: children);

  static const String name = 'QuestionnaireListRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const QuestionnaireListPage();
    },
  );
}

/// generated route for
/// [RecordDetailPage]
class RecordDetailRoute extends PageRouteInfo<RecordDetailRouteArgs> {
  RecordDetailRoute({
    required String id,
    Key? key,
    List<PageRouteInfo>? children,
  }) : super(
         RecordDetailRoute.name,
         args: RecordDetailRouteArgs(id: id, key: key),
         rawPathParams: {'id': id},
         initialChildren: children,
       );

  static const String name = 'RecordDetailRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<RecordDetailRouteArgs>(
        orElse: () => RecordDetailRouteArgs(id: pathParams.getString('id')),
      );
      return RecordDetailPage(id: args.id, key: args.key);
    },
  );
}

class RecordDetailRouteArgs {
  const RecordDetailRouteArgs({required this.id, this.key});

  final String id;

  final Key? key;

  @override
  String toString() {
    return 'RecordDetailRouteArgs{id: $id, key: $key}';
  }
}

/// generated route for
/// [RecordEditPage]
class RecordEditRoute extends PageRouteInfo<RecordEditRouteArgs> {
  RecordEditRoute({Key? key, String? id, List<PageRouteInfo>? children})
    : super(
        RecordEditRoute.name,
        args: RecordEditRouteArgs(key: key, id: id),
        rawPathParams: {'id': id},
        initialChildren: children,
      );

  static const String name = 'RecordEditRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<RecordEditRouteArgs>(
        orElse: () => RecordEditRouteArgs(id: pathParams.optString('id')),
      );
      return RecordEditPage(key: args.key, id: args.id);
    },
  );
}

class RecordEditRouteArgs {
  const RecordEditRouteArgs({this.key, this.id});

  final Key? key;

  final String? id;

  @override
  String toString() {
    return 'RecordEditRouteArgs{key: $key, id: $id}';
  }
}

/// generated route for
/// [RegisterPage]
class RegisterRoute extends PageRouteInfo<void> {
  const RegisterRoute({List<PageRouteInfo>? children})
    : super(RegisterRoute.name, initialChildren: children);

  static const String name = 'RegisterRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const RegisterPage();
    },
  );
}

/// generated route for
/// [ServiceDetailPage]
class ServiceDetailRoute extends PageRouteInfo<ServiceDetailRouteArgs> {
  ServiceDetailRoute({
    Key? key,
    required String id,
    List<PageRouteInfo>? children,
  }) : super(
         ServiceDetailRoute.name,
         args: ServiceDetailRouteArgs(key: key, id: id),
         rawPathParams: {'id': id},
         initialChildren: children,
       );

  static const String name = 'ServiceDetailRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<ServiceDetailRouteArgs>(
        orElse: () => ServiceDetailRouteArgs(id: pathParams.getString('id')),
      );
      return ServiceDetailPage(key: args.key, id: args.id);
    },
  );
}

class ServiceDetailRouteArgs {
  const ServiceDetailRouteArgs({this.key, required this.id});

  final Key? key;

  final String id;

  @override
  String toString() {
    return 'ServiceDetailRouteArgs{key: $key, id: $id}';
  }
}

/// generated route for
/// [ServiceListPage]
class ServiceListRoute extends PageRouteInfo<ServiceListRouteArgs> {
  ServiceListRoute({
    Key? key,
    required String categoryId,
    List<PageRouteInfo>? children,
  }) : super(
         ServiceListRoute.name,
         args: ServiceListRouteArgs(key: key, categoryId: categoryId),
         rawPathParams: {'categoryId': categoryId},
         initialChildren: children,
       );

  static const String name = 'ServiceListRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<ServiceListRouteArgs>(
        orElse:
            () => ServiceListRouteArgs(
              categoryId: pathParams.getString('categoryId'),
            ),
      );
      return ServiceListPage(key: args.key, categoryId: args.categoryId);
    },
  );
}

class ServiceListRouteArgs {
  const ServiceListRouteArgs({this.key, required this.categoryId});

  final Key? key;

  final String categoryId;

  @override
  String toString() {
    return 'ServiceListRouteArgs{key: $key, categoryId: $categoryId}';
  }
}

/// generated route for
/// [SettingsPage]
class SettingsRoute extends PageRouteInfo<void> {
  const SettingsRoute({List<PageRouteInfo>? children})
    : super(SettingsRoute.name, initialChildren: children);

  static const String name = 'SettingsRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const SettingsPage();
    },
  );
}

/// generated route for
/// [SuokePage]
class SuokeRoute extends PageRouteInfo<void> {
  const SuokeRoute({List<PageRouteInfo>? children})
    : super(SuokeRoute.name, initialChildren: children);

  static const String name = 'SuokeRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const SuokePage();
    },
  );
}

/// generated route for
/// [TCMTestPage]
class TCMTestRoute extends PageRouteInfo<void> {
  const TCMTestRoute({List<PageRouteInfo>? children})
    : super(TCMTestRoute.name, initialChildren: children);

  static const String name = 'TCMTestRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const TCMTestPage();
    },
  );
}

/// generated route for
/// [TopicDetailPage]
class TopicDetailRoute extends PageRouteInfo<TopicDetailRouteArgs> {
  TopicDetailRoute({
    Key? key,
    required String id,
    List<PageRouteInfo>? children,
  }) : super(
         TopicDetailRoute.name,
         args: TopicDetailRouteArgs(key: key, id: id),
         rawPathParams: {'id': id},
         initialChildren: children,
       );

  static const String name = 'TopicDetailRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<TopicDetailRouteArgs>(
        orElse: () => TopicDetailRouteArgs(id: pathParams.getString('id')),
      );
      return TopicDetailPage(key: args.key, id: args.id);
    },
  );
}

class TopicDetailRouteArgs {
  const TopicDetailRouteArgs({this.key, required this.id});

  final Key? key;

  final String id;

  @override
  String toString() {
    return 'TopicDetailRouteArgs{key: $key, id: $id}';
  }
}

/// generated route for
/// [UserAgreementPage]
class UserAgreementRoute extends PageRouteInfo<void> {
  const UserAgreementRoute({List<PageRouteInfo>? children})
    : super(UserAgreementRoute.name, initialChildren: children);

  static const String name = 'UserAgreementRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const UserAgreementPage();
    },
  );
}
