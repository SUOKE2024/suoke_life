import 'package:get/get.dart';
import 'package:suoke_life/data/models/user.dart';

class AuthService extends GetxService {
  // 当前用户
  final currentUser = Rxn<User>();
  
  // 登录状态
  final isLoggedIn = false.obs;
  
  // 初始化
  @override
  void onInit() {
    super.onInit();
    _loadCurrentUser();
  }

  // 加载当前用户
  Future<void> _loadCurrentUser() async {
    try {
      // TODO: 从本地存储或服务器获取用户信息
      final user = User(
        id: '1',
        name: '测试用户',
        avatar: 'assets/images/avatars/default.png',
      );
      currentUser.value = user;
      isLoggedIn.value = true;
    } catch (e) {
      print('加载用户信息失败: $e');
    }
  }

  // 登录
  Future<void> login(String username, String password) async {
    try {
      // TODO: 实现实际的登录逻辑
      final user = User(
        id: '1',
        name: username,
        avatar: 'assets/images/avatars/default.png',
      );
      currentUser.value = user;
      isLoggedIn.value = true;
    } catch (e) {
      throw '登录失败: $e';
    }
  }

  // 登出
  Future<void> logout() async {
    try {
      // TODO: 实现实际的登出逻辑
      currentUser.value = null;
      isLoggedIn.value = false;
    } catch (e) {
      throw '登出失败: $e';
    }
  }

  // 注册
  Future<void> register(String username, String password) async {
    try {
      // TODO: 实现实际的注册逻辑
      final user = User(
        id: '1',
        name: username,
        avatar: 'assets/images/avatars/default.png',
      );
      currentUser.value = user;
      isLoggedIn.value = true;
    } catch (e) {
      throw '注册失败: $e';
    }
  }

  // 更新用户信息
  Future<void> updateUserInfo(Map<String, dynamic> data) async {
    try {
      // TODO: 实现实际的更新逻辑
      final user = currentUser.value?.copyWith(
        name: data['name'],
        avatar: data['avatar'],
      );
      currentUser.value = user;
    } catch (e) {
      throw '更新用户信息失败: $e';
    }
  }
} 