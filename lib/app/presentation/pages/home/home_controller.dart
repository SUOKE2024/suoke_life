import '../../../core/base/base_controller.dart';

class HomeController extends BaseController {
  @override
  void initData() {
    // 初始化首页数据
  }
  
  Future<void> refreshData() async {
    try {
      showLoading();
      // 刷新数据的逻辑
      hideLoading();
    } catch (e) {
      handleError(e);
    }
  }
} 