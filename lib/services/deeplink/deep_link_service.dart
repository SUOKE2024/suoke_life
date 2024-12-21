import 'package:uni_links/uni_links.dart';
import 'package:get/get.dart';
import 'dart:async';

class DeepLinkService extends GetxService {
  StreamSubscription? _subscription;
  final _currentLink = ''.obs;

  String get currentLink => _currentLink.value;

  Future<void> init() async {
    // 处理初始链接
    try {
      final initialLink = await getInitialLink();
      if (initialLink != null) {
        _handleLink(initialLink);
      }
    } catch (e) {
      print('Error getting initial link: $e');
    }

    // 监听后续链接
    _subscription = linkStream.listen((String? link) {
      if (link != null) {
        _handleLink(link);
      }
    }, onError: (err) {
      print('Deep link error: $err');
    });
  }

  void _handleLink(String link) {
    _currentLink.value = link;
    
    // 解析链接
    final uri = Uri.parse(link);
    
    // 根据路径处理
    switch (uri.path) {
      case '/chat':
        final id = uri.queryParameters['id'];
        if (id != null) {
          Get.toNamed('/chat/$id');
        }
        break;
      case '/profile':
        Get.toNamed('/profile');
        break;
      // ... 其他路径处理
    }
  }

  @override
  void onClose() {
    _subscription?.cancel();
    super.onClose();
  }
} 