import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/life/lib/widgets/life_record_item.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

void main() {
  testWidgets('LifeRecordItem should display life record information',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        localizationsDelegates: [
          AppLocalizations.delegate,
        ],
        supportedLocales: [
          Locale('en', 'US'),
          Locale('zh', 'CN'),
        ],
        home: LifeRecordItem(
          title: 'Test Record',
          time: '10:00 AM',
          description: 'Test Description',
        ),
      ),
    );

    expect(find.text('Test Record'), findsOneWidget);
    expect(find.text('10:00 AM'), findsOneWidget);
    expect(find.text('Test Description'), findsOneWidget);
  });
}
