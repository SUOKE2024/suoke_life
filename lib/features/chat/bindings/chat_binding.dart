/// Binding for chat module dependencies.
class ChatBinding extends Binding {
  @override
  void dependencies() {
    // Services
    Get.lazyPut<ChatService>(
      () => ChatService(
        maxMessageCount: 100,
        enableVoice: true,
      ),
      fenix: true,
    );

    Get.lazyPut<MessageService>(
      () => MessageService(),
      fenix: true,
    );

    // Repositories
    Get.lazyPut<ChatRepository>(
      () => ChatRepositoryImpl(
        Get.find<NetworkService>(),
        Get.find<StorageService>(),
      ),
      fenix: true,
    );

    // Controllers
    Get.lazyPut<ChatController>(
      () => ChatController(Get.find<ChatService>()),
    );
  }
}

/// Binding for chat detail page dependencies.
class ChatDetailBinding extends Binding {
  @override
  void dependencies() {
    Get.lazyPut<ChatDetailController>(
      () => ChatDetailController(
        Get.find<ChatService>(),
        Get.find<MessageService>(),
      ),
    );
  }
} 