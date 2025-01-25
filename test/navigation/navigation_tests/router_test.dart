import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life_app_app_app/app/core/router/app_router.dart';

void main() {
  late AppRouter router;

  setUp(() {
    router = AppRouter();
  });

  testWidgets('Test navigation sequence', (tester) async {
    await tester.pumpWidget(MaterialApp.router(
      routerDelegate: router.delegate(),
      routeInformationParser: router.defaultRouteParser(),
    ));
    await tester.pumpAndSettle();

    // 1. 验证首页
    expect(find.text('首页'), findsOneWidget);
    
    // 2. 导航到 SUOKE
    await tester.tap(find.text('SUOKE'));
    await tester.pumpAndSettle();
    expect(find.text('SUOKE'), findsOneWidget);

    // 3. 导航到探索
    await tester.tap(find.text('探索'));
    await tester.pumpAndSettle();
    expect(find.text('探索'), findsOneWidget);

    // 4. 导航到 LIFE
    await tester.tap(find.text('LIFE'));
    await tester.pumpAndSettle();
    expect(find.text('LIFE'), findsOneWidget);

    // 5. 导航到我的
    await tester.tap(find.text('我的'));
    await tester.pumpAndSettle();
    expect(find.text('我的'), findsOneWidget);

    // 6. 导航到聊天页面
    router.push(ChatRoute(assistantId: 'xiaoke'));
    await tester.pumpAndSettle();
    expect(find.text('小克'), findsOneWidget);
  });
} 