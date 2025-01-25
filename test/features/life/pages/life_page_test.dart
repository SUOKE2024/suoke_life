import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/life/lib/pages/life_page.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

void main() {
  testWidgets('LifePage should display user profile, health advice, and life records',
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
        home: const LifePage(),
      ),
    );

    expect(find.byType(UserProfileCard), findsOneWidget);
    expect(find.byType(HealthAdviceCard), findsOneWidget);
    expect(find.byType(LifeRecordItem), findsWidgets);
  });
} 