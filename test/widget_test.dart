// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:suoke_app/app/routes/app_routes.dart';
import 'package:suoke_app/app/presentation/controllers/home_controller.dart';
import 'package:suoke_app/main.dart';
import 'helpers/test_helper.dart';

void main() {
  setUp(() {
    TestHelper.setupTest();
    Get.put(HomeController());
  });

  tearDown(() {
    Get.reset();
    TestHelper.clearTest();
  });

  testWidgets('App should start at home page', (tester) async {
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();

    expect(Get.currentRoute, Routes.HOME);
  });
}
