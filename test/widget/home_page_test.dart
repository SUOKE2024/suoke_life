import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:suoke_life_app_app_app/app/core/di/injection.dart';
import 'package:suoke_life_app_app_app/app/data/models/chat_message.dart';
import 'package:suoke_life_app_app_app/app/data/models/chat_info.dart';
import 'package:suoke_life_app_app_app/app/presentation/pages/home/home_page.dart';

void main() {
  setUpAll(() {
    configureDependencies();
  });

  testWidgets('HomePage shows chat list', (tester) async {
    await tester.pumpWidget(const HomePage());
    // Add your test expectations here
  });
} 