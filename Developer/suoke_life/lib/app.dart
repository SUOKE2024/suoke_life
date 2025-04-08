import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/theme/app_theme.dart';
import 'package:suoke_life/core/storage/preferences_manager.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/core/services/holistic_sensing_engine.dart';
import 'package:suoke_life/core/config/env_config.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:suoke_life/core/widgets/api_connection_status.dart';
import 'package:suoke_life/core/network/api_health_service.dart';

/// 索克生活APP主体
class SuokeApp extends ConsumerStatefulWidget {
  const SuokeApp({Key? key}) : super(key: key);

  @override
  ConsumerState<SuokeApp> createState() => _SuokeAppState();
}

class _SuokeAppState extends ConsumerState<SuokeApp> {
  @override
  void initState() {
    super.initState();
    
    // 延迟初始化区块链服务
    Future.microtask(() {
      ref.read(blockchainInitProvider);
      
      // 初始化时检查API健康状态
      ref.read(apiHealthStatusProvider);
    });
  }

  @override
  Widget build(BuildContext context) {
    // 获取路由实例
    final appRouter = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeModeProvider);

    return ScreenUtilInit(
      designSize: const Size(375, 812),
      minTextAdapt: true,
      splitScreenMode: true,
      builder: (context, child) {
        return MaterialApp.router(
          title: '索克生活',
          debugShowCheckedModeBanner: false,

          // 主题配置
          theme: AppTheme.lightTheme(),
          darkTheme: AppTheme.darkTheme(),
          themeMode: themeMode,

          // 国际化配置
          localizationsDelegates: const [
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: const [
            Locale('zh', 'CN'), // 中文简体
            Locale('en', 'US'),
          ],

          // 路由配置
          routerConfig: appRouter.config(),
          builder: (context, widget) {
            return MediaQuery(
              // 设置文本缩放比例为1.0
              data: MediaQuery.of(context).copyWith(textScaleFactor: 1.0),
              child: Overlay(
                initialEntries: [
                  OverlayEntry(
                    builder: (context) => Column(
                      children: [
                        // API连接状态栏
                        ApiConnectionStatus(
                          compact: true,
                          onRetry: () {
                            // 重试连接
                            ref.refresh(apiHealthStatusProvider);
                          },
                        ),
                        // 应用主体内容
                        Expanded(child: widget!),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}
