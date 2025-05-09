// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/app.dart';

void main() {
  testWidgets('基础应用启动测试', (WidgetTester tester) async {
    // 构建应用并触发一帧
    await tester.pumpWidget(const ProviderScope(child: SuokeLifeApp()));

    // 这里可以添加验证应用成功启动的断言
    // 例如检查标题、底部导航栏等关键元素是否存在
    expect(find.text('首页'), findsOneWidget);
    expect(find.text('SUOKE'), findsOneWidget);
    expect(find.text('探索'), findsOneWidget);
    expect(find.text('LIFE'), findsOneWidget);
    expect(find.text('我的'), findsOneWidget);
  });
}
