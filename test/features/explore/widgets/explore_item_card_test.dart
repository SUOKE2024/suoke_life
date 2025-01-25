import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/explore/lib/widgets/explore_item_card.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

void main() {
  testWidgets('ExploreItemCard should display explore item information',
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
        home: const ExploreItemCard(
          title: 'Test Item',
          description: 'Test Description',
          imageUrl: 'assets/images/yoga.jpg',
        ),
      ),
    );

    expect(find.text('Test Item'), findsOneWidget);
    expect(find.text('Test Description'), findsOneWidget);
    expect(find.byType(Image), findsOneWidget);
  });
} 