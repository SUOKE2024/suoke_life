import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ui_components/buttons/primary_button.dart';

void main() {
  testWidgets('PrimaryButton displays text and handles tap',
      (WidgetTester tester) async {
    bool wasPressed = false;

    await tester.pumpWidget(MaterialApp(
      home: PrimaryButton(
        text: '测试按钮',
        onPressed: () => wasPressed = true,
      ),
    ));

    expect(find.text('测试按钮'), findsOneWidget);

    await tester.tap(find.byType(PrimaryButton));
    expect(wasPressed, true);
  });

  testWidgets('PrimaryButton shows loading indicator when loading',
      (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(
      home: PrimaryButton(
        text: '测试按钮',
        onPressed: () {},
        isLoading: true,
      ),
    ));

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.text('测试按钮'), findsNothing);
  });
}
