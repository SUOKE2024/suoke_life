import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/life/lib/widgets/health_advice_card.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

void main() {
  testWidgets('HealthAdviceCard should display health advice',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
        ],
        supportedLocales: const [
          Locale('en', 'US'),
          Locale('zh', 'CN'),
        ],
        home: const HealthAdviceCard(),
      ),
    );

    expect(find.text('Drink plenty of water.'), findsOneWidget);
    expect(find.text('Get enough sleep.'), findsOneWidget);
    expect(find.text('Eat a balanced diet.'), findsOneWidget);
    expect(find.text('Take regular breaks during work.'), findsOneWidget);
    expect(find.text('Practice mindfulness and meditation.'), findsOneWidget);
  });
} 