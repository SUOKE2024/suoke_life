import 'package:get/get.dart';
import 'package:fluwx/fluwx.dart' as fluwx;
import 'package:tobias/tobias.dart' as tobias;
import '../models/auth_models.dart';
import 'auth_service.dart';

class ThirdPartyAuthService extends GetxService {
  static ThirdPartyAuthService get to => Get.find();
  
  final AuthService _authService = Get.find<AuthService>();
  
  // 初始化服务
  Future<ThirdPartyAuthService> init() async {
    // 初始化微信SDK
    await fluwx.registerWxApi(
      appId: "你的微信AppID",
      universalLink: "你的通用链接",
    );
    
    // 监听微信登录回调
    fluwx.weChatResponseEventHandler.listen((res) {
      if (res is fluwx.WeChatAuthResponse) {
        _handleWeChatAuthResponse(res);
      }
    });
    
    return this;
  }
  
  // 微信登录
  Future<bool> loginWithWeChat() async {
    try {
      final result = await fluwx.sendWeChatAuth(
        scope: "snsapi_userinfo",
        state: "wechat_sdk_demo",
      );
      
      if (!result) {
        throw Exception('发起微信授权失败');
      }
      
      return true;
    } catch (e) {
      Get.snackbar('错误', '微信登录失败：${e.toString()}');
      return false;
    }
  }
  
  // 处理微信登录回调
  Future<void> _handleWeChatAuthResponse(fluwx.WeChatAuthResponse response) async {
    if (response.code != null) {
      try {
        // 使用code换取access_token
        final loginResult = await _authService.loginWithWeChatCode(
          code: response.code!,
        );
        
        if (loginResult) {
          Get.offAllNamed('/main');
        } else {
          Get.snackbar('错误', '微信登录失败，请重试');
        }
      } catch (e) {
        Get.snackbar('错误', '处理微信登录失败：${e.toString()}');
      }
    } else {
      Get.snackbar('错误', '未获取到微信授权码');
    }
  }
  
  // 支付宝登录
  Future<bool> loginWithAlipay() async {
    try {
      final result = await tobias.aliPayAuth();
      
      if (result['resultStatus'] == '9000') {
        final authCode = result['result'];
        if (authCode != null) {
          final loginResult = await _authService.loginWithAlipayCode(
            code: authCode,
          );
          
          return loginResult;
        }
      }
      
      throw Exception('支付宝授权失败：${result['memo']}');
    } catch (e) {
      Get.snackbar('错误', '支付宝登录失败：${e.toString()}');
      return false;
    }
  }
  
  // 检查是否安装微信
  Future<bool> isWeChatInstalled() async {
    return await fluwx.isWeChatInstalled;
  }
  
  // 检查是否安装支付宝
  Future<bool> isAlipayInstalled() async {
    return await tobias.isAliPayInstalled();
  }
} 