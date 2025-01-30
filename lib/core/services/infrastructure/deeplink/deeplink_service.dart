import 'package:uni_links/uni_links.dart';
import 'package:rxdart/rxdart.dart';
import '../logger/logger.dart';
import 'package:auto_route/auto_route.dart';

class DeeplinkService {
  final AppLogger _logger;
  final BehaviorSubject<Uri> _deepLinkSubject;
  bool _isInitialized = false;

  DeeplinkService(this._logger)
      : _deepLinkSubject = BehaviorSubject<Uri>();

  Stream<Uri> get deepLinkStream => _deepLinkSubject.stream;

  Future<void> init() async {
    if (_isInitialized) return;

    try {
      // 处理应用未启动时的深链接
      final initialLink = await getInitialUri();
      if (initialLink != null) {
        _handleDeepLink(initialLink);
      }

      // 监听应用运行时的深链接
      uriLinkStream.listen(
        (Uri? uri) {
          if (uri != null) {
            _handleDeepLink(uri);
          }
        },
        onError: (err) {
          _logger.error('Error in deep link stream', err);
        },
      );

      _isInitialized = true;
    } catch (e, stack) {
      _logger.error('Error initializing deep link service', e, stack);
    }
  }

  void _handleDeepLink(Uri uri) {
    _logger.info('Received deep link: $uri');
    _deepLinkSubject.add(uri);
  }

  Future<void> handleRoute(Uri uri, StackRouter router) async {
    try {
      final path = uri.path;
      final params = uri.queryParameters;

      switch (path) {
        case '/chat':
          if (params.containsKey('id')) {
            await router.push(ChatDetailRoute(id: params['id']!));
          }
          break;
        case '/service':
          if (params.containsKey('id')) {
            await router.push(ServiceDetailRoute(id: params['id']!));
          }
          break;
        case '/explore':
          if (params.containsKey('topic')) {
            await router.push(TopicDetailRoute(id: params['topic']!));
          }
          break;
        default:
          _logger.warning('Unknown deep link path: $path');
      }
    } catch (e, stack) {
      _logger.error('Error handling deep link route', e, stack);
    }
  }

  void dispose() {
    _deepLinkSubject.close();
  }
} 