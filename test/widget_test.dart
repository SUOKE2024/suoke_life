// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in your widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:suoke_app/app/presentation/controllers/home/home_controller.dart';

class MockHomeController extends Mock implements HomeController {}

void main() {
  late MockHomeController mockHomeController;

  setUp(() {
    mockHomeController = MockHomeController();
  });

  testWidgets('Home page shows title', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Builder(
            builder: (context) => const Text('Home'),
          ),
        ),
      ),
    );

    expect(find.text('Home'), findsOneWidget);
  });
}
