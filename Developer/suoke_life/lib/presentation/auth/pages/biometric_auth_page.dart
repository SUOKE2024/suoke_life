import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/widgets/animated_gradient_card.dart';
import 'package:suoke_life/core/widgets/animated_press_button.dart';
import 'package:suoke_life/di/providers/auth_providers.dart';
import 'package:local_auth/local_auth.dart';
import 'package:flutter/services.dart';
import 'package:suoke_life/domain/usecases/auth_usecases.dart';

@RoutePage()
class BiometricAuthPage extends ConsumerStatefulWidget {
  const BiometricAuthPage({Key? key, this.userId}) : super(key: key);
  
  final String? userId;

  @override
  ConsumerState<BiometricAuthPage> createState() => _BiometricAuthPageState();
}

class _BiometricAuthPageState extends ConsumerState<BiometricAuthPage> {
  final LocalAuthentication _localAuth = LocalAuthentication();
  bool _canCheckBiometrics = false;
  bool _isBiometricSupported = false;
  bool _hasFaceId = false;
  bool _hasFingerprint = false;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _checkBiometrics();
  }

  Future<void> _checkBiometrics() async {
    bool canCheckBiometrics;
    try {
      canCheckBiometrics = await _localAuth.canCheckBiometrics;
    } on PlatformException catch (e) {
      canCheckBiometrics = false;
      setState(() {
        _errorMessage = '无法检查生物识别功能: ${e.message}';
      });
    }

    bool isBiometricSupported;
    try {
      isBiometricSupported = await _localAuth.isDeviceSupported();
    } on PlatformException catch (e) {
      isBiometricSupported = false;
      setState(() {
        _errorMessage = '设备不支持生物识别: ${e.message}';
      });
    }

    List<BiometricType> availableBiometrics = [];
    try {
      availableBiometrics = await _localAuth.getAvailableBiometrics();
    } on PlatformException catch (e) {
      setState(() {
        _errorMessage = '无法获取可用的生物识别类型: ${e.message}';
      });
    }

    setState(() {
      _canCheckBiometrics = canCheckBiometrics;
      _isBiometricSupported = isBiometricSupported;
      _hasFaceId = availableBiometrics.contains(BiometricType.face);
      _hasFingerprint = availableBiometrics.contains(BiometricType.fingerprint) ||
                        availableBiometrics.contains(BiometricType.strong) ||
                        availableBiometrics.contains(BiometricType.weak);
    });
  }

  Future<void> _authenticateWithBiometrics() async {
    if (!_canCheckBiometrics || !_isBiometricSupported) {
      setState(() {
        _errorMessage = '您的设备不支持生物识别';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final didAuthenticate = await _localAuth.authenticate(
        localizedReason: '请使用生物识别进行身份验证',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: true,
        ),
      );

      if (didAuthenticate) {
        // 生物识别成功，获取token
        final userId = widget.userId ?? '';
        
        // 调用验证方法
        try {
          final biometricToken = _generateBiometricToken();
          await ref.read(authStateProvider.notifier).verifyBiometric(userId, biometricToken);
          
          // 检查验证结果
          final authState = ref.read(authStateProvider);
          if (authState.isAuthenticated) {
            if (mounted) {
              // 验证成功，跳转到主页
              context.router.replace(const MainDashboardRoute());
            }
          } else if (authState.error != null) {
            setState(() {
              _errorMessage = authState.error;
            });
          }
        } catch (e) {
          setState(() {
            _errorMessage = '生物识别验证失败: ${e.toString()}';
          });
        }
      } else {
        setState(() {
          _errorMessage = '生物识别验证失败';
        });
      }
    } on PlatformException catch (e) {
      setState(() {
        _errorMessage = '生物识别错误: ${e.message}';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  // 生成生物识别临时令牌
  String _generateBiometricToken() {
    // 实际应用中，这里应该生成一个安全的令牌
    // 这里仅作示例，返回一个固定值
    return 'bio_token_${DateTime.now().millisecondsSinceEpoch}';
  }

  // 切换到密码登录
  void _switchToPasswordLogin() {
    context.router.replace(const LoginRoute());
  }

  // 注册新的生物识别
  Future<void> _registerBiometric() async {
    if (!_canCheckBiometrics || !_isBiometricSupported) {
      setState(() {
        _errorMessage = '您的设备不支持生物识别';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final didAuthenticate = await _localAuth.authenticate(
        localizedReason: '请使用生物识别进行身份验证以注册',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: true,
        ),
      );

      if (didAuthenticate) {
        final userId = widget.userId ?? '';
        String biometricType = 'fingerprint';
        
        if (_hasFaceId) {
          biometricType = 'faceId';
        } else if (_hasFingerprint) {
          biometricType = 'fingerprint';
        }
        
        // 调用注册方法
        try {
          final success = await ref.read(authRepositoryProvider).registerBiometric(userId, biometricType);
          
          if (success) {
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('生物识别注册成功')),
              );
              // 立即尝试使用新注册的生物识别认证
              _authenticateWithBiometrics();
            }
          } else {
            setState(() {
              _errorMessage = '生物识别注册失败';
            });
          }
        } catch (e) {
          setState(() {
            _errorMessage = '生物识别注册失败: ${e.toString()}';
          });
        }
      } else {
        setState(() {
          _errorMessage = '生物识别验证失败';
        });
      }
    } on PlatformException catch (e) {
      setState(() {
        _errorMessage = '生物识别错误: ${e.message}';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);
    
    // 如果已经在认证状态管理器中设置了loading状态，使用它
    _isLoading = authState.isLoading;
    
    // 如果有错误信息，显示它
    if (authState.error != null) {
      _errorMessage = authState.error;
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('生物识别登录'),
        centerTitle: true,
        elevation: 0,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Logo和应用名称
              Image.asset(
                'assets/images/logo.png',
                width: 80,
                height: 80,
              ),
              const SizedBox(height: 12),
              const Text(
                '索克生活',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                '您的健康生活管理专家',
                style: TextStyle(
                  fontSize: 16,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 40),
              
              // 生物识别卡片
              AnimatedGradientCard(
                colors: const [
                  Color(0xFF35BB78), // 索克绿
                  Color.fromARGB(255, 53, 187, 149),
                  Color.fromARGB(255, 53, 140, 187),
                ],
                borderRadius: BorderRadius.circular(16),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: [
                      // 图标与标题
                      Icon(
                        _hasFaceId 
                            ? Icons.face_outlined
                            : (_hasFingerprint 
                                ? Icons.fingerprint
                                : Icons.lock_outlined),
                        size: 64,
                        color: Colors.white,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        _hasFaceId 
                            ? '面容ID登录'
                            : (_hasFingerprint 
                                ? '指纹登录'
                                : '生物识别登录'),
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _hasFaceId || _hasFingerprint
                            ? '使用生物识别可以更快地登录应用'
                            : '您的设备不支持生物识别功能，请使用密码登录',
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.white,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 32),
              
              // 认证部分
              SizedBox(
                width: double.infinity,
                child: Card(
                  elevation: 2,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        const Text(
                          '请使用生物识别登录',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _hasFaceId || _hasFingerprint
                              ? '使用生物识别可以更快地登录应用'
                              : '您的设备不支持生物识别功能，请使用密码登录',
                          style: const TextStyle(
                            fontSize: 14,
                            color: Colors.black54,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        
                        const SizedBox(height: 24),
                        
                        // 错误信息
                        if (_errorMessage != null)
                          Container(
                            padding: const EdgeInsets.all(10),
                            margin: const EdgeInsets.only(bottom: 16),
                            width: double.infinity,
                            decoration: BoxDecoration(
                              color: AppColors.errorColor.withAlpha(30),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              _errorMessage!,
                              style: TextStyle(
                                color: AppColors.errorColor,
                                fontSize: 14,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        
                        // 验证按钮
                        if (_hasFaceId || _hasFingerprint)
                          AnimatedPressButton(
                            onPressed: _isLoading ? null : _authenticateWithBiometrics,
                            child: _isLoading
                                ? const SizedBox(
                                    height: 20,
                                    width: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Colors.white,
                                    ),
                                  )
                                : const Text(
                                    '使用生物识别',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                          ),
                        
                        const SizedBox(height: 16),
                        
                        // 注册生物识别按钮
                        if (_hasFaceId || _hasFingerprint)
                          OutlinedButton(
                            onPressed: _isLoading ? null : _registerBiometric,
                            style: OutlinedButton.styleFrom(
                              foregroundColor: AppColors.primaryColor,
                              side: BorderSide(color: AppColors.primaryColor),
                              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                            child: const Text('注册新的生物识别'),
                          ),
                          
                        const SizedBox(height: 16),
                        
                        // 使用密码登录
                        TextButton(
                          onPressed: _switchToPasswordLogin,
                          child: Text(
                            '使用密码登录',
                            style: TextStyle(
                              color: AppColors.primaryColor,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 