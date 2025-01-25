import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ui_components/dialogs/app_dialog.dart';

void main() {
  testWidgets('AppDialog UI test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) => ElevatedButton(
            onPressed: () {
              showDialog(
                context: context,
                builder: (context) => const AppDialog(
                  title: 'Test Dialog',
                  content: 'This is a test dialog.',
                ),
              );
            },
            child: const Text('Show Dialog'),
          ),
        ),
      ),
    );

    // Tap the button to show the dialog
    await tester.tap(find.text('Show Dialog'));
    await tester.pumpAndSettle();

    // Verify that the dialog is displayed
    expect(find.byType(AlertDialog), findsOneWidget);
    expect(find.text('Test Dialog'), findsOneWidget);
    expect(find.text('This is a test dialog.'), findsOneWidget);
  });
}
