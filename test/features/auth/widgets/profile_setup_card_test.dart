import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/auth/lib/widgets/profile_setup_card.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

void main() {
  testWidgets('ProfileSetupCard should display registration form',
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
        home: const ProfileSetupCard(),
      ),
    );

    expect(find.text('Username'), findsOneWidget);
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
    expect(find.text('Register'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(3));
    expect(find.byType(ElevatedButton), findsOneWidget);
  });
} 