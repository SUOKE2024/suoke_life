class AppRoutesManager {
  static final instance = AppRoutesManager._();
  AppRoutesManager._();

  final _routes = <GetPage>[];
  final _moduleRoutes = <String, List<GetPage>>{};

  void registerModuleRoutes(AppModule module) {
    final routes = module.routes();
    _moduleRoutes[module.name] = routes;
    _routes.addAll(routes);
  }

  List<GetPage> get routes => _routes;

  List<GetPage>? getModuleRoutes(String moduleName) {
    return _moduleRoutes[moduleName];
  }

  void clearRoutes() {
    _routes.clear();
    _moduleRoutes.clear();
  }
} 