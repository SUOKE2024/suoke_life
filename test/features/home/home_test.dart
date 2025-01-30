import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/home/pages/home_page.dart';
import 'package:suoke_life/features/home/controllers/home_controller.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

void main() {
  setUpAll(() async {
    await dotenv.load(fileName: "/Users/songxu/Developer/suoke_life/.env");
    print('App Name: \\${dotenv.env['APP_NAME']}');
  });

  group('Home Module Tests', () {
    testWidgets('HomePage displays title and main components', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(
        home: HomePage(),
      ));

      expect(find.text('首页'), findsOneWidget);
      expect(find.byKey(Key('health_status_card')), findsOneWidget);
      expect(find.byKey(Key('quick_action_grid')), findsOneWidget);
    });

    test('HomeController changePage updates currentIndex', () {
      final controller = HomeController();
      controller.changePage(1);
      expect(controller.currentIndex.value, 1);
    });

    test('HomeController refreshData handles data refresh', () async {
      final controller = HomeController();
      await controller.refreshData();
      // Add assertions to verify data refresh logic
    });
  });
} 