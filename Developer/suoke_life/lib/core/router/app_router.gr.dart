// dart format width=80
// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// AutoRouterGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

part of 'app_router.dart';

/// generated route for
/// [AccountSecurityPage]
class AccountSecurityPageRoute extends PageRouteInfo<void> {
  const AccountSecurityPageRoute({List<PageRouteInfo>? children})
    : super(AccountSecurityPageRoute.name, initialChildren: children);

  static const String name = 'AccountSecurityPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const AccountSecurityPage();
    },
  );
}

/// generated route for
/// [ApiTestPage]
class ApiTestPageRoute extends PageRouteInfo<void> {
  const ApiTestPageRoute({List<PageRouteInfo>? children})
    : super(ApiTestPageRoute.name, initialChildren: children);

  static const String name = 'ApiTestPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const ApiTestPage();
    },
  );
}

/// generated route for
/// [BiometricAuthPage]
class BiometricAuthPageRoute extends PageRouteInfo<BiometricAuthPageRouteArgs> {
  BiometricAuthPageRoute({
    Key? key,
    String? userId,
    List<PageRouteInfo>? children,
  }) : super(
         BiometricAuthPageRoute.name,
         args: BiometricAuthPageRouteArgs(key: key, userId: userId),
         initialChildren: children,
       );

  static const String name = 'BiometricAuthPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<BiometricAuthPageRouteArgs>(
        orElse: () => const BiometricAuthPageRouteArgs(),
      );
      return BiometricAuthPage(key: args.key, userId: args.userId);
    },
  );
}

class BiometricAuthPageRouteArgs {
  const BiometricAuthPageRouteArgs({this.key, this.userId});

  final Key? key;

  final String? userId;

  @override
  String toString() {
    return 'BiometricAuthPageRouteArgs{key: $key, userId: $userId}';
  }
}

/// generated route for
/// [BlockchainPage]
class BlockchainPageRoute extends PageRouteInfo<void> {
  const BlockchainPageRoute({List<PageRouteInfo>? children})
    : super(BlockchainPageRoute.name, initialChildren: children);

  static const String name = 'BlockchainPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const BlockchainPage();
    },
  );
}

/// generated route for
/// [ChatPage]
class ChatPageRoute extends PageRouteInfo<ChatPageRouteArgs> {
  ChatPageRoute({
    Key? key,
    required String contactName,
    required String contactAvatar,
    bool isAI = false,
    List<PageRouteInfo>? children,
  }) : super(
         ChatPageRoute.name,
         args: ChatPageRouteArgs(
           key: key,
           contactName: contactName,
           contactAvatar: contactAvatar,
           isAI: isAI,
         ),
         initialChildren: children,
       );

  static const String name = 'ChatPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<ChatPageRouteArgs>();
      return ChatPage(
        key: args.key,
        contactName: args.contactName,
        contactAvatar: args.contactAvatar,
        isAI: args.isAI,
      );
    },
  );
}

class ChatPageRouteArgs {
  const ChatPageRouteArgs({
    this.key,
    required this.contactName,
    required this.contactAvatar,
    this.isAI = false,
  });

  final Key? key;

  final String contactName;

  final String contactAvatar;

  final bool isAI;

  @override
  String toString() {
    return 'ChatPageRouteArgs{key: $key, contactName: $contactName, contactAvatar: $contactAvatar, isAI: $isAI}';
  }
}

/// generated route for
/// [ConstitutionAssessmentPage]
class ConstitutionAssessmentPageRoute extends PageRouteInfo<void> {
  const ConstitutionAssessmentPageRoute({List<PageRouteInfo>? children})
    : super(ConstitutionAssessmentPageRoute.name, initialChildren: children);

  static const String name = 'ConstitutionAssessmentPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const ConstitutionAssessmentPage();
    },
  );
}

/// generated route for
/// [ConstitutionResultPage]
class ConstitutionResultPageRoute
    extends PageRouteInfo<ConstitutionResultPageRouteArgs> {
  ConstitutionResultPageRoute({
    Key? key,
    required ConstitutionData constitutionData,
    List<PageRouteInfo>? children,
  }) : super(
         ConstitutionResultPageRoute.name,
         args: ConstitutionResultPageRouteArgs(
           key: key,
           constitutionData: constitutionData,
         ),
         initialChildren: children,
       );

  static const String name = 'ConstitutionResultPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<ConstitutionResultPageRouteArgs>();
      return ConstitutionResultPage(
        key: args.key,
        constitutionData: args.constitutionData,
      );
    },
  );
}

class ConstitutionResultPageRouteArgs {
  const ConstitutionResultPageRouteArgs({
    this.key,
    required this.constitutionData,
  });

  final Key? key;

  final ConstitutionData constitutionData;

  @override
  String toString() {
    return 'ConstitutionResultPageRouteArgs{key: $key, constitutionData: $constitutionData}';
  }
}

/// generated route for
/// [ExplorationDetailPage]
class ExplorationDetailPageRoute
    extends PageRouteInfo<ExplorationDetailPageRouteArgs> {
  ExplorationDetailPageRoute({
    Key? key,
    required ExplorationItem item,
    List<PageRouteInfo>? children,
  }) : super(
         ExplorationDetailPageRoute.name,
         args: ExplorationDetailPageRouteArgs(key: key, item: item),
         initialChildren: children,
       );

  static const String name = 'ExplorationDetailPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<ExplorationDetailPageRouteArgs>();
      return ExplorationDetailPage(key: args.key, item: args.item);
    },
  );
}

class ExplorationDetailPageRouteArgs {
  const ExplorationDetailPageRouteArgs({this.key, required this.item});

  final Key? key;

  final ExplorationItem item;

  @override
  String toString() {
    return 'ExplorationDetailPageRouteArgs{key: $key, item: $item}';
  }
}

/// generated route for
/// [ExplorePage]
class ExplorePageRoute extends PageRouteInfo<void> {
  const ExplorePageRoute({List<PageRouteInfo>? children})
    : super(ExplorePageRoute.name, initialChildren: children);

  static const String name = 'ExplorePageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const ExplorePage();
    },
  );
}

/// generated route for
/// [HealthProfilePage]
class HealthProfilePageRoute extends PageRouteInfo<void> {
  const HealthProfilePageRoute({List<PageRouteInfo>? children})
    : super(HealthProfilePageRoute.name, initialChildren: children);

  static const String name = 'HealthProfilePageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const HealthProfilePage();
    },
  );
}

/// generated route for
/// [HealthRegimenPage]
class HealthRegimenPageRoute extends PageRouteInfo<HealthRegimenPageRouteArgs> {
  HealthRegimenPageRoute({
    Key? key,
    required String constitutionTypeStr,
    List<PageRouteInfo>? children,
  }) : super(
         HealthRegimenPageRoute.name,
         args: HealthRegimenPageRouteArgs(
           key: key,
           constitutionTypeStr: constitutionTypeStr,
         ),
         initialChildren: children,
       );

  static const String name = 'HealthRegimenPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<HealthRegimenPageRouteArgs>();
      return HealthRegimenPage(
        key: args.key,
        constitutionTypeStr: args.constitutionTypeStr,
      );
    },
  );
}

class HealthRegimenPageRouteArgs {
  const HealthRegimenPageRouteArgs({
    this.key,
    required this.constitutionTypeStr,
  });

  final Key? key;

  final String constitutionTypeStr;

  @override
  String toString() {
    return 'HealthRegimenPageRouteArgs{key: $key, constitutionTypeStr: $constitutionTypeStr}';
  }
}

/// generated route for
/// [HomePage]
class HomePageRoute extends PageRouteInfo<void> {
  const HomePageRoute({List<PageRouteInfo>? children})
    : super(HomePageRoute.name, initialChildren: children);

  static const String name = 'HomePageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const HomePage();
    },
  );
}

/// generated route for
/// [KnowledgeArticleDetailPage]
class KnowledgeArticleDetailPageRoute
    extends PageRouteInfo<KnowledgeArticleDetailPageRouteArgs> {
  KnowledgeArticleDetailPageRoute({
    Key? key,
    required String articleId,
    List<PageRouteInfo>? children,
  }) : super(
         KnowledgeArticleDetailPageRoute.name,
         args: KnowledgeArticleDetailPageRouteArgs(
           key: key,
           articleId: articleId,
         ),
         rawPathParams: {'articleId': articleId},
         initialChildren: children,
       );

  static const String name = 'KnowledgeArticleDetailPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final pathParams = data.inheritedPathParams;
      final args = data.argsAs<KnowledgeArticleDetailPageRouteArgs>(
        orElse:
            () => KnowledgeArticleDetailPageRouteArgs(
              articleId: pathParams.getString('articleId'),
            ),
      );
      return KnowledgeArticleDetailPage(
        key: args.key,
        articleId: args.articleId,
      );
    },
  );
}

class KnowledgeArticleDetailPageRouteArgs {
  const KnowledgeArticleDetailPageRouteArgs({
    this.key,
    required this.articleId,
  });

  final Key? key;

  final String articleId;

  @override
  String toString() {
    return 'KnowledgeArticleDetailPageRouteArgs{key: $key, articleId: $articleId}';
  }
}

/// generated route for
/// [KnowledgeGraphViewer]
class KnowledgeGraphViewerRoute
    extends PageRouteInfo<KnowledgeGraphViewerRouteArgs> {
  KnowledgeGraphViewerRoute({
    Key? key,
    String? initialNodeId,
    VisualizationMode mode = VisualizationMode.mode3D,
    List<PageRouteInfo>? children,
  }) : super(
         KnowledgeGraphViewerRoute.name,
         args: KnowledgeGraphViewerRouteArgs(
           key: key,
           initialNodeId: initialNodeId,
           mode: mode,
         ),
         initialChildren: children,
       );

  static const String name = 'KnowledgeGraphViewerRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<KnowledgeGraphViewerRouteArgs>(
        orElse: () => const KnowledgeGraphViewerRouteArgs(),
      );
      return KnowledgeGraphViewer(
        key: args.key,
        initialNodeId: args.initialNodeId,
        mode: args.mode,
      );
    },
  );
}

class KnowledgeGraphViewerRouteArgs {
  const KnowledgeGraphViewerRouteArgs({
    this.key,
    this.initialNodeId,
    this.mode = VisualizationMode.mode3D,
  });

  final Key? key;

  final String? initialNodeId;

  final VisualizationMode mode;

  @override
  String toString() {
    return 'KnowledgeGraphViewerRouteArgs{key: $key, initialNodeId: $initialNodeId, mode: $mode}';
  }
}

/// generated route for
/// [LifePage]
class LifePageRoute extends PageRouteInfo<void> {
  const LifePageRoute({List<PageRouteInfo>? children})
    : super(LifePageRoute.name, initialChildren: children);

  static const String name = 'LifePageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const LifePage();
    },
  );
}

/// generated route for
/// [LoginPage]
class LoginPageRoute extends PageRouteInfo<LoginPageRouteArgs> {
  LoginPageRoute({
    Key? key,
    void Function()? onLoginSuccess,
    List<PageRouteInfo>? children,
  }) : super(
         LoginPageRoute.name,
         args: LoginPageRouteArgs(key: key, onLoginSuccess: onLoginSuccess),
         initialChildren: children,
       );

  static const String name = 'LoginPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<LoginPageRouteArgs>(
        orElse: () => const LoginPageRouteArgs(),
      );
      return LoginPage(key: args.key, onLoginSuccess: args.onLoginSuccess);
    },
  );
}

class LoginPageRouteArgs {
  const LoginPageRouteArgs({this.key, this.onLoginSuccess});

  final Key? key;

  final void Function()? onLoginSuccess;

  @override
  String toString() {
    return 'LoginPageRouteArgs{key: $key, onLoginSuccess: $onLoginSuccess}';
  }
}

/// generated route for
/// [MainDashboardPage]
class MainDashboardPageRoute extends PageRouteInfo<void> {
  const MainDashboardPageRoute({List<PageRouteInfo>? children})
    : super(MainDashboardPageRoute.name, initialChildren: children);

  static const String name = 'MainDashboardPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const MainDashboardPage();
    },
  );
}

/// generated route for
/// [MainPage]
class MainPageRoute extends PageRouteInfo<void> {
  const MainPageRoute({List<PageRouteInfo>? children})
    : super(MainPageRoute.name, initialChildren: children);

  static const String name = 'MainPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const MainPage();
    },
  );
}

/// generated route for
/// [NetworkTestRoute]
class NetworkTestRouteRoute extends PageRouteInfo<void> {
  const NetworkTestRouteRoute({List<PageRouteInfo>? children})
    : super(NetworkTestRouteRoute.name, initialChildren: children);

  static const String name = 'NetworkTestRouteRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const NetworkTestRoute();
    },
  );
}

/// generated route for
/// [NotFoundPage]
class NotFoundPageRoute extends PageRouteInfo<void> {
  const NotFoundPageRoute({List<PageRouteInfo>? children})
    : super(NotFoundPageRoute.name, initialChildren: children);

  static const String name = 'NotFoundPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const NotFoundPage();
    },
  );
}

/// generated route for
/// [ProfilePage]
class ProfilePageRoute extends PageRouteInfo<void> {
  const ProfilePageRoute({List<PageRouteInfo>? children})
    : super(ProfilePageRoute.name, initialChildren: children);

  static const String name = 'ProfilePageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const ProfilePage();
    },
  );
}

/// generated route for
/// [PulseDiagnosisPage]
class PulseDiagnosisPageRoute extends PageRouteInfo<void> {
  const PulseDiagnosisPageRoute({List<PageRouteInfo>? children})
    : super(PulseDiagnosisPageRoute.name, initialChildren: children);

  static const String name = 'PulseDiagnosisPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const PulseDiagnosisPage();
    },
  );
}

/// generated route for
/// [RagSearchPage]
class RagSearchPageRoute extends PageRouteInfo<RagSearchPageRouteArgs> {
  RagSearchPageRoute({
    Key? key,
    String initialQuery = '',
    String searchType = 'general',
    List<PageRouteInfo>? children,
  }) : super(
         RagSearchPageRoute.name,
         args: RagSearchPageRouteArgs(
           key: key,
           initialQuery: initialQuery,
           searchType: searchType,
         ),
         initialChildren: children,
       );

  static const String name = 'RagSearchPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<RagSearchPageRouteArgs>(
        orElse: () => const RagSearchPageRouteArgs(),
      );
      return RagSearchPage(
        key: args.key,
        initialQuery: args.initialQuery,
        searchType: args.searchType,
      );
    },
  );
}

class RagSearchPageRouteArgs {
  const RagSearchPageRouteArgs({
    this.key,
    this.initialQuery = '',
    this.searchType = 'general',
  });

  final Key? key;

  final String initialQuery;

  final String searchType;

  @override
  String toString() {
    return 'RagSearchPageRouteArgs{key: $key, initialQuery: $initialQuery, searchType: $searchType}';
  }
}

/// generated route for
/// [RegisterPage]
class RegisterPageRoute extends PageRouteInfo<void> {
  const RegisterPageRoute({List<PageRouteInfo>? children})
    : super(RegisterPageRoute.name, initialChildren: children);

  static const String name = 'RegisterPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const RegisterPage();
    },
  );
}

/// generated route for
/// [SensingControlPage]
class SensingControlPageRoute extends PageRouteInfo<void> {
  const SensingControlPageRoute({List<PageRouteInfo>? children})
    : super(SensingControlPageRoute.name, initialChildren: children);

  static const String name = 'SensingControlPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const SensingControlPage();
    },
  );
}

/// generated route for
/// [SuokePage]
class SuokePageRoute extends PageRouteInfo<void> {
  const SuokePageRoute({List<PageRouteInfo>? children})
    : super(SuokePageRoute.name, initialChildren: children);

  static const String name = 'SuokePageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const SuokePage();
    },
  );
}

/// generated route for
/// [ThemeSettingsPage]
class ThemeSettingsPageRoute extends PageRouteInfo<void> {
  const ThemeSettingsPageRoute({List<PageRouteInfo>? children})
    : super(ThemeSettingsPageRoute.name, initialChildren: children);

  static const String name = 'ThemeSettingsPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const ThemeSettingsPage();
    },
  );
}

/// generated route for
/// [TongueDiagnosisPage]
class TongueDiagnosisPageRoute
    extends PageRouteInfo<TongueDiagnosisPageRouteArgs> {
  TongueDiagnosisPageRoute({
    Key? key,
    String? imagePath,
    List<PageRouteInfo>? children,
  }) : super(
         TongueDiagnosisPageRoute.name,
         args: TongueDiagnosisPageRouteArgs(key: key, imagePath: imagePath),
         initialChildren: children,
       );

  static const String name = 'TongueDiagnosisPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<TongueDiagnosisPageRouteArgs>(
        orElse: () => const TongueDiagnosisPageRouteArgs(),
      );
      return TongueDiagnosisPage(key: args.key, imagePath: args.imagePath);
    },
  );
}

class TongueDiagnosisPageRouteArgs {
  const TongueDiagnosisPageRouteArgs({this.key, this.imagePath});

  final Key? key;

  final String? imagePath;

  @override
  String toString() {
    return 'TongueDiagnosisPageRouteArgs{key: $key, imagePath: $imagePath}';
  }
}

/// generated route for
/// [TwoFactorAuthPage]
class TwoFactorAuthPageRoute extends PageRouteInfo<TwoFactorAuthPageRouteArgs> {
  TwoFactorAuthPageRoute({
    Key? key,
    String? temporaryToken,
    List<PageRouteInfo>? children,
  }) : super(
         TwoFactorAuthPageRoute.name,
         args: TwoFactorAuthPageRouteArgs(
           key: key,
           temporaryToken: temporaryToken,
         ),
         initialChildren: children,
       );

  static const String name = 'TwoFactorAuthPageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      final args = data.argsAs<TwoFactorAuthPageRouteArgs>(
        orElse: () => const TwoFactorAuthPageRouteArgs(),
      );
      return TwoFactorAuthPage(
        key: args.key,
        temporaryToken: args.temporaryToken,
      );
    },
  );
}

class TwoFactorAuthPageRouteArgs {
  const TwoFactorAuthPageRouteArgs({this.key, this.temporaryToken});

  final Key? key;

  final String? temporaryToken;

  @override
  String toString() {
    return 'TwoFactorAuthPageRouteArgs{key: $key, temporaryToken: $temporaryToken}';
  }
}

/// generated route for
/// [WelcomePage]
class WelcomePageRoute extends PageRouteInfo<void> {
  const WelcomePageRoute({List<PageRouteInfo>? children})
    : super(WelcomePageRoute.name, initialChildren: children);

  static const String name = 'WelcomePageRoute';

  static PageInfo page = PageInfo(
    name,
    builder: (data) {
      return const WelcomePage();
    },
  );
}
