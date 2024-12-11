import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import '../controllers/login_controller.dart';
import '../widgets/phone_input.dart';
import '../../core/routes/route_lifecycle.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends BasePageState<LoginPage> {
  late final LoginController controller;
  
  @override
  void initState() {
    super.initState();
    controller = Get.put(LoginController());
  }
  
  @override
  Widget buildPage(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('登录'),
        centerTitle: true,
        actions: [
          // 生物识别登录按钮
          Obx(() {
            if (controller.supportsBiometric) {
              return IconButton(
                icon: const Icon(Icons.fingerprint),
                onPressed: controller.loginWithBiometric,
                tooltip: '指纹/面容登录',
              );
            }
            return const SizedBox.shrink();
          }),
          // 声纹登录按钮
          Obx(() {
            if (controller.supportsVoice) {
              return IconButton(
                icon: const Icon(Icons.mic),
                onPressed: controller.loginWithVoice,
                tooltip: '声纹登录',
              );
            }
            return const SizedBox.shrink();
          }),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(16.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(height: 40.h),
              // Logo
              Center(
                child: Image.asset(
                  'assets/images/logo.png',
                  width: 120.w,
                  height: 120.w,
                ),
              ),
              SizedBox(height: 40.h),
              // 手机号输入
              PhoneInput(
                controller: controller.phoneController,
                onChanged: (value) => setState(() {}),
              ),
              SizedBox(height: 16.h),
              // 验证码输入
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: controller.codeController,
                      keyboardType: TextInputType.number,
                      maxLength: 6,
                      decoration: const InputDecoration(
                        labelText: '验证码',
                        hintText: '请输入验证码',
                        counterText: '',
                      ),
                      onChanged: (value) => setState(() {}),
                    ),
                  ),
                  SizedBox(width: 16.w),
                  Obx(() => SizedBox(
                    width: 120.w,
                    child: ElevatedButton(
                      onPressed: controller.canGetCode
                          ? controller.sendVerificationCode
                          : null,
                      child: Text(
                        controller.canGetCode
                            ? '获取验证码'
                            : '${controller.countdown}s',
                      ),
                    ),
                  )),
                ],
              ),
              SizedBox(height: 16.h),
              // 自动登录选项
              Row(
                children: [
                  Obx(() => Checkbox(
                    value: controller.rememberLogin,
                    onChanged: (value) {
                      if (value != null) {
                        controller.toggleRememberLogin(value);
                      }
                    },
                  )),
                  Text(
                    '自动登录',
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
              SizedBox(height: 24.h),
              // 登录按钮
              Obx(() => ElevatedButton(
                onPressed: _canLogin() ? controller.login : null,
                child: controller.isLoading
                    ? const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            Colors.white,
                          ),
                        ),
                      )
                    : const Text('登录'),
              )),
              SizedBox(height: 32.h),
              // 分割线
              Row(
                children: [
                  Expanded(child: Divider(color: Colors.grey[300])),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16.w),
                    child: Text(
                      '其他登录方式',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 14.sp,
                      ),
                    ),
                  ),
                  Expanded(child: Divider(color: Colors.grey[300])),
                ],
              ),
              SizedBox(height: 24.h),
              // 第三方登录按钮
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildThirdPartyButton(
                    'assets/images/wechat.png',
                    '微信登录',
                    controller.loginWithWeChat,
                  ),
                  SizedBox(width: 48.w),
                  _buildThirdPartyButton(
                    'assets/images/alipay.png',
                    '支付宝登录',
                    controller.loginWithAlipay,
                  ),
                ],
              ),
              SizedBox(height: 32.h),
              // 隐私政策和服务条款
              DefaultTextStyle(
                style: Theme.of(context).textTheme.bodySmall!,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('登录即表示同意'),
                    TextButton(
                      onPressed: controller.toPrivacyPolicy,
                      child: const Text('隐私政策'),
                    ),
                    const Text('和'),
                    TextButton(
                      onPressed: controller.toTermsOfService,
                      child: const Text('服务条款'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildThirdPartyButton(
    String iconPath,
    String label,
    VoidCallback onPressed,
  ) {
    return Column(
      children: [
        IconButton(
          icon: Image.asset(
            iconPath,
            width: 40.w,
            height: 40.w,
          ),
          onPressed: onPressed,
        ),
        SizedBox(height: 8.h),
        Text(
          label,
          style: TextStyle(
            fontSize: 12.sp,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }
  
  bool _canLogin() {
    if (controller.isLoading) return false;
    final phone = controller.phoneController.text.trim();
    final code = controller.codeController.text.trim();
    return phone.isNotEmpty && code.length == 6;
  }
  
  @override
  void onPageStart() {
    super.onPageStart();
    // 检查是否有重定向路由
    final redirectRoute = Get.parameters['redirect'];
    if (redirectRoute != null && redirectRoute.isNotEmpty) {
      Get.snackbar(
        '提示',
        '请先登录后继续访问',
        duration: const Duration(seconds: 2),
      );
    }
  }
} 