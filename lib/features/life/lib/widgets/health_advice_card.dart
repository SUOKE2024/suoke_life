import 'package:flutter/material.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

class HealthAdviceCard extends StatelessWidget {
  const HealthAdviceCard({Key? key}) : super(key: key);

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
              localizations.translate('health_advice'),
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(localizations.translate('drink_water')),
            const SizedBox(height: 8),
            Text(localizations.translate('get_sleep')),
            const SizedBox(height: 8),
            Text(localizations.translate('eat_diet')),
            const SizedBox(height: 8),
            Text('Take regular breaks during work.'),
            const SizedBox(height: 8),
            Text('Practice mindfulness and meditation.'),
          ],
        ),
      ),
    );
  }
} 