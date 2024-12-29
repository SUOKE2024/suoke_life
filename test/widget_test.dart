// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in your widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:suoke_app/app/core/database/database_helper.dart';
import 'package:suoke_app/app/core/services/network/network_service.dart';
import 'package:suoke_app/app/services/features/ai/assistants/xiaoi_service.dart';
import 'package:suoke_app/app/presentation/pages/home/home_page.dart';
import 'package:suoke_app/app/core/services/storage/storage_service.dart';
import 'package:suoke_app/app/presentation/controllers/home/home_controller.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';
import 'package:suoke_app/app/presentation/controllers/suoke/suoke_controller.dart';
import 'package:suoke_app/app/presentation/controllers/explore/explore_controller.dart';
import 'package:suoke_app/app/presentation/controllers/life/life_controller.dart';
import 'package:suoke_app/app/presentation/controllers/profile/profile_controller.dart';
import 'package:suoke_app/app/presentation/controllers/chat/chat_controller.dart';

import 'mocks/mock_storage_service.dart';
import 'mocks/mock_home_controller.dart';
import 'mocks/mock_network_service.dart';
import 'mocks/mock_xiaoi_service.dart';
import 'mocks/mock_suoke_service.dart';
import 'mocks/mock_database_helper.dart';
import 'mocks/mock_suoke_controller.dart';
import 'mocks/mock_explore_controller.dart';
import 'mocks/mock_life_controller.dart';
import 'mocks/mock_profile_controller.dart';
import 'mocks/mock_chat_controller.dart';

void main() {
  late MockStorageService mockStorage;
  late MockHomeController mockHomeController;
  late MockChatController mockChatController;
  late MockNetworkService mockNetwork;
  late MockXiaoiService mockXiaoiService;
  late MockSuokeService mockSuokeService;
  late MockSuokeController mockSuokeController;
  late MockExploreController mockExploreController;
  late MockLifeController mockLifeController;
  late MockProfileController mockProfileController;

  setUp(() {
    Get.reset();
    mockStorage = MockStorageService();
    mockSuokeService = MockSuokeService();
    
    // 创建所有 mock controllers
    mockHomeController = MockHomeController(suokeService: mockSuokeService);
    mockChatController = MockChatController(suokeService: mockSuokeService);
    mockSuokeController = MockSuokeController(suokeService: mockSuokeService);
    mockExploreController = MockExploreController(suokeService: mockSuokeService);
    mockLifeController = MockLifeController(suokeService: mockSuokeService);
    mockProfileController = MockProfileController(suokeService: mockSuokeService);

    // 注册所有 controllers
    Get.put<HomeController>(mockHomeController, permanent: true);
    Get.put<ChatController>(mockChatController, permanent: true);
    Get.put<SuokeController>(mockSuokeController, permanent: true);
    Get.put<ExploreController>(mockExploreController, permanent: true);
    Get.put<LifeController>(mockLifeController, permanent: true);
    Get.put<ProfileController>(mockProfileController, permanent: true);
  });

  tearDown(() async {
    await mockStorage.dispose();
    Get.reset();
  });

  testWidgets('Counter increments smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      GetMaterialApp(
        home: const HomePage(),
        initialBinding: BindingsBuilder(() {
          // 确保所有依赖都已注册
          Get.put<HomeController>(mockHomeController);
          Get.put<SuokeController>(mockSuokeController);
          Get.put<ExploreController>(mockExploreController);
          Get.put<LifeController>(mockLifeController);
        }),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.byType(HomePage), findsOneWidget);
    expect(mockHomeController.currentIndex.value, 0);
  });
}
