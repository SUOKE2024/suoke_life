import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/pages/home/home_page.dart';
import 'package:suoke_app/app/presentation/controllers/home_controller.dart';
import '../helpers/test_helper.dart';

void main() {
  late HomeController homeController;

  setUp(() {
    homeController = Get.put(HomeController());
  });

  tearDown(() {
    Get.reset();
  });

  testWidgets('HomePage navigation test', (WidgetTester tester) async {
    await tester.pumpWidget(
      GetMaterialApp(
        home: HomePage(),
      ),
    );

    expect(find.byType(HomePage), findsOneWidget);
    expect(homeController.currentIndex.value, 0);

    await tester.tap(find.byIcon(Icons.person));
    await tester.pump();
    
    expect(homeController.currentIndex.value, 2);
  });
} 