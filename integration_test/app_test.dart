import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:suoke_app/main.dart' as app;
import '../test/helpers/test_helper.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('App Test', () {
    testWidgets('App launch test', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // 验证应用成功启动
      expect(find.byType(app.MyApp), findsOneWidget);
    });

    testWidgets('AI Chat test', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // 导航到 AI 聊天页面
      await tester.tap(find.byIcon(Icons.chat));
      await tester.pumpAndSettle();

      // 输入消息
      await tester.enterText(find.byType(TextField), 'Hello AI');
      await tester.tap(find.byIcon(Icons.send));
      await tester.pumpAndSettle();

      // 验证响应
      expect(find.text('Hello AI'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });
  });
} 