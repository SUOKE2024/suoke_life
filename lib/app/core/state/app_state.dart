class AppState extends GetxController {
  static AppState get to => Get.find();
  
  final isLoading = false.obs;
  final currentUser = Rxn<User>();
  final appSettings = Rxn<AppSettings>();
  
  Future<void> initialize() async {
    // 初始化应用状态
  }
} 