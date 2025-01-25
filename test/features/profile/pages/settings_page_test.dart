import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/profile/lib/pages/settings_page.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

void main() {
  testWidgets('SettingsPage should display settings options',
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
        home: const SettingsPage(),
      ),
    );

    expect(find.text('Notifications'), findsOneWidget);
    expect(find.text('Privacy'), findsOneWidget);
    expect(find.text('About'), findsOneWidget);
    expect(find.text('Edit Profile'), findsOneWidget);
    expect(find.text('Admin Dashboard'), findsOneWidget);
  });
} 