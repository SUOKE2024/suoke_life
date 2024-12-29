import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';

class HomeController extends GetxController {
  final SuokeService suokeService;
  final currentIndex = 0.obs;
  final isLoading = false.obs;
  final errorMessage = ''.obs;

  // 添加缓存机制
  final _cache = <String, dynamic>{}.obs;

  HomeController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    ever(currentIndex, (_) => _handlePageChange);
    _initializeData();
  }

  Future<void> _handlePageChange(int index) async {
    // 预加载下一页数据
    try {
      switch(index) {
        case 1: // SUOKE
          if (!_cache.containsKey('suoke_services')) {
            final services = await suokeService.getServices();
            _cache['suoke_services'] = services;
          }
          break;
        case 2: // 探索
          if (!_cache.containsKey('knowledge_graph')) {
            final graph = await suokeService.getKnowledgeGraph('default');
            _cache['knowledge_graph'] = graph;
          }
          break;
        // ... 其他页面预加载
      }
    } catch (e) {
      errorMessage.value = e.toString();
    }
  }

  // 添加错误处理和重试机制
  Future<void> retry() async {
    isLoading.value = true;
    try {
      await _initializeData();
      errorMessage.value = '';
    } catch (e) {
      errorMessage.value = e.toString();
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> _initializeData() async {
    try {
      // 初始化服务
      await suokeService.init();
      
      // 检查用户状态
      final user = await suokeService.getCurrentUser();
      if (user == null) {
        Get.offNamed('/login');
        return;
      }

      // 加载配置
      await _loadConfigurations();
      
    } catch (e) {
      Get.snackbar('错误', '初始化失败: ${e.toString()}');
    }
  }

  void changePage(int index) {
    currentIndex.value = index;
  }

  Future<void> _loadConfigurations() async {
    // TODO: 加载用户配置、主题设置等
  }
} 