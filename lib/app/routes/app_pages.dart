import 'package:get/get.dart';
import '../presentation/pages/home/home_page.dart';
import '../presentation/pages/chat/chat_detail_page.dart';
import '../presentation/bindings/home_binding.dart';
import '../presentation/bindings/chat_binding.dart';
import '../presentation/pages/ai/ai_chat_page.dart';
import '../presentation/bindings/ai_chat_binding.dart';
import '../presentation/pages/ai/assistant_select_page.dart';
import '../presentation/pages/ai/assistant_chat_page.dart';

part 'app_routes.dart';

class AppPages {
  static const INITIAL = Routes.HOME;

  static final routes = [
    GetPage(
      name: Routes.HOME,
      page: () => const HomePage(),
      binding: HomeBinding(),
    ),
    GetPage(
      name: Routes.AI_CHAT,
      page: () => const AiChatPage(),
      binding: AiChatBinding(),
    ),
    GetPage(
      name: Routes.CHAT_DETAIL,
      page: () => const ChatDetailPage(),
      binding: ChatBinding(),
    ),
    GetPage(
      name: '/assistants',
      page: () => const AssistantSelectPage(),
    ),
    GetPage(
      name: '/chat/detail',
      page: () => AssistantChatPage(
        conversation: Get.arguments as ChatConversation,
      ),
    ),
  ];
} 