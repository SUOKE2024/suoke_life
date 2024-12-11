class AppPages {
  static final routes = [
    GetPage(
      name: Routes.SPLASH,
      page: () => const SplashPage(),
      binding: SplashBinding(),
    ),
    ...AuthPages.routes,
    ...ChatPages.routes,
    ...AIPages.routes,
    ...GamePages.routes,
  ];
} 