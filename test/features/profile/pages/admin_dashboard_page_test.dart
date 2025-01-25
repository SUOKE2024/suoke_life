import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/profile/lib/pages/admin_dashboard_page.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

void main() {
  testWidgets('AdminDashboardPage should display admin dashboard content',
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
        home: const AdminDashboardPage(),
      ),
    );

    expect(find.text('Admin Dashboard Content'), findsOneWidget);
  });
} 