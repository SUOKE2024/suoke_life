import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'core/utils/constants.dart';
import 'core/router/app_router.dart';
import 'di/providers/theme_providers.dart';
import 'di/providers/locale_providers.dart';

/// 索克生活应用主体
class SuokeLifeApp extends ConsumerWidget {
  /// 构造函数
  const SuokeLifeApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appRouter = ref.watch(appRouterProvider);
    final themeData = ref.watch(themeDataProvider);
    final themeMode = ref.watch(themeModeProvider);
    final locale = ref.watch(localeProvider);

    return MaterialApp.router(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      
      // 主题设置
      theme: themeData,
      themeMode: themeMode,
      
      // 国际化配置
      locale: locale,
      supportedLocales: const [
        Locale('zh', 'CN'),
        Locale('en', 'US'),
      ],
      localizationsDelegates: const [
        // AppLocalizations.delegate, // TODO: 实现本地化
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      
      // 路由配置
      routerConfig: appRouter,
      
      // 全局滚动行为
      scrollBehavior: const ScrollBehavior().copyWith(
        physics: const BouncingScrollPhysics(),
      ),
    );
  }
} 