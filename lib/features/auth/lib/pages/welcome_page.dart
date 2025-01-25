import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:suoke_life/features/auth/lib/widgets/profile_setup_card.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

class WelcomePage extends StatelessWidget {
  const WelcomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Welcome'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                localizations.translate('welcome_title'),
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                localizations.translate('welcome_message'),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () => context.go('/login'),
                child: Text(localizations.translate('login_button')),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  // TODO: Implement registration logic
                  context.go('/profile');
                },
                child: Text(localizations.translate('register_button')),
              ),
              const SizedBox(height: 16),
              const ProfileSetupCard(),
            ],
          ),
        ),
      ),
    );
  }
} 