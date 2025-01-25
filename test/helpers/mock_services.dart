import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/services/doubao_service.dart';
import 'package:suoke_app/app/services/chat_service.dart';
import 'package:suoke_app/app/services/auth_service.dart';
import 'package:suoke_app/app/services/storage_service.dart';
import 'package:get/get.dart';

class MockDouBaoService extends Mock implements DouBaoService {}
class MockChatService extends Mock implements ChatService {}
class MockAuthService extends Mock implements AuthService {}
class MockStorageService extends Mock implements StorageService {}

void setupMockServices() {
  final mockDouBaoService = MockDouBaoService();
  final mockChatService = MockChatService();
  final mockAuthService = MockAuthService();
  final mockStorageService = MockStorageService();

  // 设置默认行为
  when(mockAuthService.isLoggedIn).thenReturn(true.obs);
  when(mockChatService.getConversations()).thenAnswer((_) async => []);
  
  // 注入 mock 服务
  Get.put<DouBaoService>(mockDouBaoService);
  Get.put<ChatService>(mockChatService);
  Get.put<AuthService>(mockAuthService);
  Get.put<StorageService>(mockStorageService);
} 