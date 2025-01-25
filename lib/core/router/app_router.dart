import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:suoke_life/features/home/lib/chat_page.dart';
import 'package:suoke_life/features/home/lib/chat_interaction_page.dart';
import 'package:suoke_life/features/suoke/lib/pages/suoke_page.dart';
import 'package:suoke_life/features/explore/lib/pages/explore_page.dart';
import 'package:suoke_life/features/life/lib/pages/life_page.dart';
import 'package:suoke_life/features/profile/lib/pages/settings_page.dart';
import 'package:suoke_life/features/auth/lib/pages/login_page.dart';
import 'package:suoke_life/features/auth/lib/pages/welcome_page.dart';
import 'package:suoke_life/features/profile/lib/pages/edit_profile_page.dart';
import 'package:suoke_life/features/profile/lib/pages/admin_dashboard_page.dart';
import 'package:suoke_life/ui_components/welcome_page.dart';
import 'package:suoke_life/features/profile/lib/pages/health_data_input_page.dart';

class AppRouter {
  static final router = GoRouter(
    initialLocation: '/welcome',
    routes: [
      GoRoute(
        path: '/welcome',
        builder: (context, state) => const WelcomePage(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const ChatPage(),
      ),
      GoRoute(
        path: '/suoke',
        builder: (context, state) => const SuokePage(),
      ),
      GoRoute(
        path: '/explore',
        builder: (context, state) => const ExplorePage(),
      ),
      GoRoute(
        path: '/life',
        builder: (context, state) => const LifePage(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsPage(),
      ),
      GoRoute(
        path: '/edit_profile',
        builder: (context, state) => const EditProfilePage(),
      ),
      GoRoute(
        path: '/admin_dashboard',
        builder: (context, state) => const AdminDashboardPage(),
      ),
      GoRoute(
        path: '/health_data_input',
        builder: (context, state) => const HealthDataInputPage(),
      ),
    ],
  );

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case '/':
        return MaterialPageRoute(builder: (_) => const WelcomePage());
      case '/login':
        return MaterialPageRoute(builder: (_) => const LoginPage());
      case '/home':
        return MaterialPageRoute(builder: (_) => const ChatPage());
      case '/chat_interaction':
        return MaterialPageRoute(builder: (_) => const ChatInteractionPage());
      case '/life':
        return MaterialPageRoute(builder: (_) => const LifePage());
      case '/profile/settings':
        return MaterialPageRoute(builder: (_) => const SettingsPage());
      case '/profile/edit':
        return MaterialPageRoute(builder: (_) => const EditProfilePage());
      case '/suoke':
        return MaterialPageRoute(builder: (_) => const SuokePage());
      case '/suoke/detail':
        return MaterialPageRoute(builder: (_) => const ServiceDetailPage());
      case '/explore':
        return MaterialPageRoute(builder: (_) => const ExplorePage());
      case '/explore/detail':
        return MaterialPageRoute(builder: (_) => const ExploreItemDetailPage());
      default:
        return MaterialPageRoute(
          builder: (_) => Scaffold(
            body: Center(
              child: Text('No route defined for ${settings.name}'),
            ),
          ),
        );
    }
  }
} 