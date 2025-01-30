class DeepLinkHandler {
  static final instance = DeepLinkHandler._();
  DeepLinkHandler._();

  final _eventBus = Get.find<EventBus>();
  final _initialLink = Rxn<String>();
  final _currentLink = Rxn<String>();
  
  StreamSubscription? _linkSubscription;
  final _routes = <String, DeepLinkRoute>{};

  Future<void> initialize() async {
    try {
      // 获取初始链接
      final initialLink = await getInitialLink();
      if (initialLink != null) {
        _handleDeepLink(initialLink);
        _initialLink.value = initialLink;
      }

      // 监听新的深链接
      _linkSubscription = uriLinkStream.listen((Uri? uri) {
        if (uri != null) {
          final link = uri.toString();
          _handleDeepLink(link);
          _currentLink.value = link;
        }
      });
    } catch (e) {
      LoggerManager.instance.error('Deep link initialization failed', e);
    }
  }

  void registerRoute(DeepLinkRoute route) {
    _routes[route.pattern] = route;
  }

  void _handleDeepLink(String link) {
    try {
      final uri = Uri.parse(link);
      final path = uri.path;
      final params = uri.queryParameters;

      // 查找匹配的路由
      final route = _findMatchingRoute(path);
      if (route != null) {
        _eventBus.fire(DeepLinkReceivedEvent(
          path: path,
          params: params,
          route: route,
        ));
        
        // 执行路由处理
        route.handler(DeepLinkData(
          path: path,
          params: params,
          originalLink: link,
        ));
      }
    } catch (e) {
      LoggerManager.instance.error('Deep link handling failed', e);
    }
  }

  DeepLinkRoute? _findMatchingRoute(String path) {
    return _routes.values.firstWhereOrNull(
      (route) => RegExp(route.pattern).hasMatch(path),
    );
  }

  String? get initialLink => _initialLink.value;
  String? get currentLink => _currentLink.value;

  void dispose() {
    _linkSubscription?.cancel();
    _routes.clear();
  }
}

class DeepLinkRoute {
  final String pattern;
  final String name;
  final Function(DeepLinkData) handler;

  DeepLinkRoute({
    required this.pattern,
    required this.name,
    required this.handler,
  });
}

class DeepLinkData {
  final String path;
  final Map<String, String> params;
  final String originalLink;

  DeepLinkData({
    required this.path,
    required this.params,
    required this.originalLink,
  });
}

class DeepLinkReceivedEvent extends AppEvent {
  final String path;
  final Map<String, String> params;
  final DeepLinkRoute route;

  DeepLinkReceivedEvent({
    required this.path,
    required this.params,
    required this.route,
  });
} 