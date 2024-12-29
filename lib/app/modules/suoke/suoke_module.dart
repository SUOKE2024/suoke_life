class SuokeModule extends FeatureModule {
  @override
  String get name => 'suoke';
  
  @override
  String get featureKey => 'SUOKE';

  @override
  SuokeService? get service => Get.find<SuokeService>();

  @override
  SuokeController? get controller => Get.find<SuokeController>();

  @override
  List<GetPage> get pages => [
    GetPage(
      name: Routes.SUOKE,
      page: () => const SuokePage(),
      binding: SuokeBinding(),
    ),
    // 其他相关页面...
  ];

  @override
  List<Bindings> get bindings => [
    SuokeBinding(),
  ];

  @override
  Future<void> init() async {
    Get.lazyPut(() => SuokeService());
    Get.lazyPut(() => SuokeController(Get.find()));
  }
} 