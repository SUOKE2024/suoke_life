class MiddlewareManager {
  static final instance = MiddlewareManager._();
  MiddlewareManager._();

  final _middlewares = <String, List<GetMiddleware>>{};

  void registerMiddleware(String route, GetMiddleware middleware) {
    _middlewares.putIfAbsent(route, () => []).add(middleware);
  }

  void registerModuleMiddlewares(AppModule module) {
    // 注册模块级别的中间件
    final moduleMiddlewares = module.middlewares();
    moduleMiddlewares.forEach((route, middleware) {
      registerMiddleware(route, middleware);
    });
  }

  List<GetMiddleware> getMiddlewares(String route) {
    return _middlewares[route] ?? [];
  }
} 