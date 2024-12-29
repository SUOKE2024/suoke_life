import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/pages/home/home_page.dart';
import 'package:suoke_app/app/presentation/controllers/home/home_controller.dart';
import 'package:suoke_app/app/presentation/controllers/chat/chat_controller.dart';
import 'package:suoke_app/app/presentation/controllers/suoke/suoke_controller.dart';
import 'package:suoke_app/app/presentation/controllers/explore/explore_controller.dart';
import 'package:suoke_app/app/presentation/controllers/life/life_controller.dart';
import 'package:suoke_app/app/presentation/controllers/profile/profile_controller.dart';
import '../mocks/mock_home_controller.dart';
import '../mocks/mock_chat_controller.dart';
import '../mocks/mock_suoke_controller.dart';
import '../mocks/mock_explore_controller.dart';
import '../mocks/mock_life_controller.dart';
import '../mocks/mock_profile_controller.dart';
import '../mocks/mock_suoke_service.dart';

void main() {
  late MockHomeController mockHomeController;
  late MockChatController mockChatController;
  late MockSuokeController mockSuokeController;
  late MockExploreController mockExploreController;
  late MockLifeController mockLifeController;
  late MockProfileController mockProfileController;
  late MockSuokeService mockSuokeService;

  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
    Get.reset();
    mockSuokeService = MockSuokeService();
    
    // 创建所有 mock controllers
    mockHomeController = MockHomeController(suokeService: mockSuokeService);
    mockChatController = MockChatController(suokeService: mockSuokeService);
    mockSuokeController = MockSuokeController(suokeService: mockSuokeService);
    mockExploreController = MockExploreController(suokeService: mockSuokeService);
    mockLifeController = MockLifeController(suokeService: mockSuokeService);
    mockProfileController = MockProfileController(suokeService: mockSuokeService);

    // 注册所有 controllers
    Get.put<HomeController>(mockHomeController);
    Get.put<ChatController>(mockChatController);
    Get.put<SuokeController>(mockSuokeController);
    Get.put<ExploreController>(mockExploreController);
    Get.put<LifeController>(mockLifeController);
    Get.put<ProfileController>(mockProfileController);
  });

  testWidgets('HomePage should display bottom navigation bar', (WidgetTester tester) async {
    await tester.pumpWidget(
      GetMaterialApp(
        home: const HomePage(),
      ),
    );

    await tester.pumpAndSettle();

    // 验证底部导航栏存在
    expect(find.byType(BottomNavigationBar), findsOneWidget);

    // 验证导航项
    final bottomNavBar = tester.widget<BottomNavigationBar>(find.byType(BottomNavigationBar));
    expect(bottomNavBar.items.length, 5);

    // 验证导航项的标签
    expect(bottomNavBar.items[0].label, '消息');
    expect(bottomNavBar.items[1].label, 'SUOKE');
    expect(bottomNavBar.items[2].label, '探索');
    expect(bottomNavBar.items[3].label, 'LIFE');
    expect(bottomNavBar.items[4].label, '我的');

    // 测试导航功能
    // 找到 BottomNavigationBar 的位置
    final navBarFinder = find.byType(BottomNavigationBar);
    final navBarRect = tester.getRect(navBarFinder);
    
    // 计算每个导航项的位置
    final itemWidth = navBarRect.width / 5;
    
    // 点击 SUOKE (第二个项目)
    await tester.tapAt(Offset(
      navBarRect.left + itemWidth * 1.5, // 第二个项目的中心
      navBarRect.center.dy,
    ));
    await tester.pumpAndSettle();
    expect(mockHomeController.currentIndex.value, 1);

    // 点击探索 (第三个项目)
    await tester.tapAt(Offset(
      navBarRect.left + itemWidth * 2.5, // 第三个项目的中心
      navBarRect.center.dy,
    ));
    await tester.pumpAndSettle();
    expect(mockHomeController.currentIndex.value, 2);
  });

  tearDown(() {
    Get.reset();
  });
} 