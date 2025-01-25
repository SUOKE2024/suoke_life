import 'package:flutter_test/flutter_test.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life_app_app_app/app/core/router/router_config.dart';

void main() {
  group('Router Tests', () {
    late AppRouter router;
    
    setUp(() {
      router = AppRouter();
    });
    
    test('should have correct route paths', () {
      final routes = router.routes;
      
      // 验证主要路由路径
      expect(routes.any((r) => r.name == 'MainRoute'), isTrue);
      expect(routes.any((r) => r.name == 'ChatRoute'), isTrue);
    });
    
    test('should have correct child routes', () {
      final mainRoute = router.routes.firstWhere((r) => r.name == 'MainRoute');
      final children = mainRoute.children;
      
      expect(children, hasLength(5));
      expect(children.map((r) => r.name), containsAll([
        'HomeRoute',
        'SuokeRoute',
        'ExploreRoute',
        'LifeRoute',
        'ProfileRoute',
      ]));
    });
  });
} 