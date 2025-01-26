import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:suoke_life/core/di/modules/database_module.dart';
import 'package:suoke_life/core/di/modules/storage_module.dart'
    as storage_module;
import 'package:suoke_life/core/router/app_router.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';
import 'package:suoke_life/features/home/lib/chat_page.dart';
import 'package:suoke_life/features/suoke/lib/pages/suoke_page.dart';
import 'package:suoke_life/features/explore/lib/pages/explore_page.dart';
import 'package:suoke_life/features/life/lib/pages/life_page.dart';
import 'package:suoke_life/features/profile/lib/pages/settings_page.dart';
import 'package:suoke_life/features/profile/lib/pages/edit_profile_page.dart';
import 'package:suoke_life/features/profile/lib/pages/admin_dashboard_page.dart';
import 'package:suoke_life/features/auth/lib/pages/welcome_page.dart';
import 'package:suoke_life/features/auth/lib/pages/login_page.dart';
import 'package:go_router/go_router.dart';
import 'package:suoke_life/core/di/injection.dart';
import 'package:suoke_life/core/utils/error_handler.dart';
import 'package:suoke_life/core/services/infrastructure/redis_service.dart';
import 'package:suoke_life/core/services/ai_service.dart';
import 'package:suoke_life/core/di/modules/network_module.dart'
    as network_module;
import 'package:get_it/get_it.dart';
import 'package:suoke_life/core/services/infrastructure/database_service.dart';

final getIt = GetIt.instance;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: '.env');
  configureDependencies();
  await DatabaseModule().register(getIt);
  storage_module.registerStorageModule(getIt);
  network_module.registerNetworkModule(getIt);
  getIt.registerSingleton<RedisService>(RedisService());
  getIt.registerSingleton<AiService>(AiService());

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Suoke Life',
      routerConfig: AppRouter.router,
      debugShowCheckedModeBanner: false,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en', 'US'),
        Locale('zh', 'CN'),
      ],
      localeResolutionCallback: (locale, supportedLocales) {
        for (var supportedLocale in supportedLocales) {
          if (supportedLocale.languageCode == locale?.languageCode &&
              supportedLocale.countryCode == locale?.countryCode) {
            return supportedLocale;
          }
        }
        return supportedLocales.first;
      },
      onGenerateTitle: (context) =>
          AppLocalizations.of(context)!.translate('app_title'),
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      builder: (context, child) {
        return ErrorHandler(child: child!);
      },
    );
  }
}
