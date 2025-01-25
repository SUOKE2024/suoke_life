import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/suoke/lib/pages/suoke_page.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

void main() {
  testWidgets('SuokePage should display service list and search field',
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
        home: const SuokePage(),
      ),
    );

    expect(find.byType(TextField), findsOneWidget);
    expect(find.byType(ServiceCard), findsWidgets);
  });

  testWidgets('SuokePage should filter services based on search query',
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
        home: const SuokePage(),
      ),
    );

    await tester.enterText(find.byType(TextField), 'Yoga');
    await tester.pumpAndSettle();

    expect(find.text('Yoga Class'), findsOneWidget);
    expect(find.text('Massage Therapy'), findsNothing);
  });
} 