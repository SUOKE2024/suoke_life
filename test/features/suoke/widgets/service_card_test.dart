import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/suoke/lib/widgets/service_card.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

void main() {
  testWidgets('ServiceCard should display service information',
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
        home: const ServiceCard(
          title: 'Test Service',
          description: 'Test Description',
          imageUrl: 'assets/images/yoga.jpg',
        ),
      ),
    );

    expect(find.text('Test Service'), findsOneWidget);
    expect(find.text('Test Description'), findsOneWidget);
    expect(find.byType(Image), findsOneWidget);
  });
} 