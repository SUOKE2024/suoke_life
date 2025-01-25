import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

class ProfileSetupCard extends StatelessWidget {
  const ProfileSetupCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              localizations.translate('complete_profile'),
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(localizations.translate('setup_profile')),
            const SizedBox(height: 16),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton(
                onPressed: () => context.go('/profile'),
                child: Text(localizations.translate('account')),
              ),
            ),
          ],
        ),
      ),
    );
  }
} 