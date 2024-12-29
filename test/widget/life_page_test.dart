import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/pages/life/life_page.dart';
import 'package:suoke_app/app/presentation/controllers/life/life_controller.dart';
import 'package:suoke_app/app/presentation/widgets/user_profile_card.dart';
import 'package:suoke_app/app/presentation/widgets/health_advice_list.dart';
import 'package:suoke_app/app/presentation/widgets/life_record_grid.dart';
import '../mocks/mock_life_controller.dart';
import '../mocks/mock_suoke_service.dart';

void main() {
  late MockLifeController mockLifeController;
  late MockSuokeService mockSuokeService;

  setUp(() {
    mockSuokeService = MockSuokeService();
    mockLifeController = MockLifeController(suokeService: mockSuokeService);
    Get.put<LifeController>(mockLifeController);
  });

  testWidgets('LifePage should display all widgets', (WidgetTester tester) async {
    await tester.pumpWidget(
      GetMaterialApp(
        home: const LifePage(),
      ),
    );

    await tester.pump();

    expect(find.byType(UserProfileCard), findsOneWidget);
    expect(find.byType(HealthAdviceList), findsOneWidget);
    expect(find.byType(LifeRecordGrid), findsOneWidget);
  });

  tearDown(() {
    Get.reset();
  });
} 