class CoreModule extends BaseModule {
  @override
  void registerDependencies() {
    // 基础服务
    Get.put(AppConfig(), permanent: true);
    Get.put(StorageService(), permanent: true);
    Get.put(LoggerService(), permanent: true);
    
    // 网络服务
    Get.put(NetworkService(), permanent: true);
    Get.put(ApiClient(), permanent: true);
    
    // 认证服务
    Get.put(AuthService(), permanent: true);
    Get.put(SecurityService(), permanent: true);
  }
  
  @override
  List<Binding> bindings() => [
    CoreBinding(),
    NetworkBinding(),
    StorageBinding(),
  ];
} 