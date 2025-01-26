import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/suoke/lib/pages/service_detail_page.dart';

void main() {
  testWidgets('ServiceDetailPage should display service details',
      (WidgetTester tester) async {
    const title = 'Test Service';
    const description = 'This is a test service description.';
    const imageUrl = 'assets/images/test_image.jpg';

    await tester.pumpWidget(
      const MaterialApp(
        home: ServiceDetailPage(
          title: title,
          description: description,
          imageUrl: imageUrl,
        ),
      ),
    );

    expect(find.text(title), findsOneWidget);
    expect(find.text(description), findsOneWidget);
    expect(find.byType(Image), findsOneWidget);
  });
}
