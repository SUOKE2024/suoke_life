import 'package:flutter/material.dart';
import 'core/di/injection.dart';
import 'presentation/pages/home/home_page.dart';
import 'presentation/controllers/home/home_controller.dart';
import 'presentation/pages/chat/chat_detail_page.dart';
import 'presentation/controllers/chat/chat_detail_controller.dart';
import 'presentation/pages/explore/topic_detail_page.dart';
import 'presentation/controllers/explore/topic_detail_controller.dart';
import 'presentation/controllers/life/record_detail_controller.dart';
import 'presentation/pages/profile/edit_profile_page.dart';
import 'presentation/controllers/profile/edit_profile_controller.dart';
import 'presentation/pages/settings/settings_page.dart';
import 'presentation/controllers/settings/settings_controller.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Suoke App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: HomePage(
        controller: getIt<HomeController>(),
      ),
      onGenerateRoute: (settings) {
        switch (settings.name) {
          case '/chat/detail':
            return MaterialPageRoute(
              builder: (context) => ChatDetailPage(
                controller: getIt<ChatDetailController>(),
              ),
            );
          case '/explore/topic':
            return MaterialPageRoute(
              builder: (context) => TopicDetailPage(
                controller: getIt<TopicDetailController>(),
              ),
            );
          case '/life/record':
            return MaterialPageRoute(
              builder: (context) => LifeRecordDetailPage(
                controller: getIt<LifeRecordDetailController>(),
              ),
            );
          case '/profile/edit':
            return MaterialPageRoute(
              builder: (context) => EditProfilePage(
                controller: getIt<EditProfileController>(),
              ),
            );
          case '/settings':
            return MaterialPageRoute(
              builder: (context) => SettingsPage(
                controller: getIt<SettingsController>(),
              ),
            );
          default:
            return MaterialPageRoute(
              builder: (context) => const Scaffold(
                body: Center(child: Text('Page not found')),
              ),
            );
        }
      },
    );
  }
}
