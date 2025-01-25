class AppRoutes {
  static final routes = [
    GetPage(
      name: Routes.HOME,
      page: () => const HomePage(),
      binding: HomeBinding(),
      middlewares: [AuthMiddleware()],
    ),
    // ... 其他路由
  ];
  
  static const INITIAL = Routes.SPLASH;
} 