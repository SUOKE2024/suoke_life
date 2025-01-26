import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/explore/lib/pages/explore_item_detail_page.dart';

void main() {
  testWidgets('ExploreItemDetailPage should display explore item details',
      (WidgetTester tester) async {
    const title = 'Test Explore Item';
    const description = 'This is a test explore item description.';
    const imageUrl = 'assets/images/test_image.jpg';

    await tester.pumpWidget(
      const MaterialApp(
        home: ExploreItemDetailPage(
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
