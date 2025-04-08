import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/di/providers/auth_providers.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/domain/usecases/auth_usecases.dart';
import 'package:suoke_life/core/widgets/animated_gradient_card.dart';

/// 账户安全页面
@RoutePage()
class AccountSecurityPage extends ConsumerStatefulWidget {
  const AccountSecurityPage({Key? key}) : super(key: key);
  
  @override
  ConsumerState<AccountSecurityPage> createState() => _AccountSecurityPageState();
}

class _AccountSecurityPageState extends ConsumerState<AccountSecurityPage> {
  bool _is2FAEnabled = false;
  String _2FAMethod = '';
  bool _isBiometricEnabled = false;
  bool _isLoading = true;
  List<SuspiciousLoginAttempt> _suspiciousLogins = [];
  Map<String, bool> _linkedAccounts = {};
  PasswordSecurityResult? _passwordSecurity;
  
  @override
  void initState() {
    super.initState();
    _loadSecurityData();
  }
  
  /// 加载安全数据
  Future<void> _loadSecurityData() async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      final authState = ref.read(authStateProvider);
      final authUseCases = ref.read(authUseCasesProvider);
      
      if (authState.isAuthenticated && authState.user != null) {
        // 获取认证详情
        final authDetails = await authUseCases.getAuthStatusDetails();
        
        // 获取可疑登录
        final suspiciousLogins = await authUseCases.detectSuspiciousLogins();
        
        // 获取社交账号连接状态
        final linkedAccounts = await authUseCases.getLinkedSocialAccounts();
        
        setState(() {
          _is2FAEnabled = authDetails.is2FAEnabled;
          _2FAMethod = authDetails.twoFactorMethod;
          _isBiometricEnabled = authDetails.isBiometricEnabled;
          _suspiciousLogins = suspiciousLogins;
          _linkedAccounts = linkedAccounts;
          _isLoading = false;
        });
      } else {
        // 未登录，重定向到登录页面
        context.router.replace(const LoginRoute());
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('加载安全数据失败: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  /// 检查密码安全性
  Future<void> _checkPasswordSecurity() async {
    // 显示密码输入对话框
    final password = await _showPasswordPrompt(
      context, 
      '输入当前密码',
      '为了检查密码安全性，请输入您当前的密码'
    );
    
    if (password != null && password.isNotEmpty) {
      setState(() {
        _isLoading = true;
      });
      
      try {
        final authUseCases = ref.read(authUseCasesProvider);
        final result = await authUseCases.checkPasswordSecurity(password);
        
        setState(() {
          _passwordSecurity = result;
          _isLoading = false;
        });
        
        // 显示密码安全性结果
        _showPasswordSecurityResult(result);
      } catch (e) {
        setState(() {
          _isLoading = false;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('检查密码安全性失败: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
  
  /// 显示密码安全性结果
  void _showPasswordSecurityResult(PasswordSecurityResult result) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Text(
                    '密码安全性评估',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              
              // 安全性评分
              Row(
                children: [
                  Icon(
                    result.isSecure 
                        ? Icons.security 
                        : Icons.security_update_warning,
                    color: result.isSecure 
                        ? Colors.green 
                        : Colors.orange,
                    size: 28,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    '安全评分: ${result.score}/5',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w500,
                      color: result.isSecure 
                          ? Colors.green 
                          : Colors.orange,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              
              // 密码是否泄露
              if (result.isBreached) ...[
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.red.withAlpha(30),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Colors.red.withAlpha(100),
                      width: 1,
                    ),
                  ),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.warning_amber_rounded,
                        color: Colors.red,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              '警告: 此密码已泄露',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.red,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '该密码已在${result.breachCount}次数据泄露事件中出现，请立即更换。',
                              style: const TextStyle(
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],
              
              // 安全性建议
              if (result.suggestions.isNotEmpty) ...[
                const Text(
                  '提高安全性的建议:',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 8),
                ...result.suggestions.map((suggestion) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(
                        Icons.check_circle_outline,
                        size: 18,
                        color: AppColors.primary,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(suggestion),
                      ),
                    ],
                  ),
                )),
                const SizedBox(height: 8),
              ],
              
              // 最后检查时间
              if (result.lastChecked != null) ...[
                const Divider(),
                const SizedBox(height: 8),
                Text(
                  '最后检查时间: ${_formatDateTime(result.lastChecked!)}',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
              
              const SizedBox(height: 24),
              
              // 更新密码按钮
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    context.router.push(const ChangePasswordRoute());
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('更新密码'),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
  
  /// 格式化日期时间
  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inDays < 1) {
      return '今天 ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays < 2) {
      return '昨天 ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else {
      return '${dateTime.year}-${dateTime.month.toString().padLeft(2, '0')}-${dateTime.day.toString().padLeft(2, '0')} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    }
  }
  
  /// 显示密码输入对话框
  Future<String?> _showPasswordPrompt(
    BuildContext context, 
    String title, 
    String message
  ) async {
    final TextEditingController controller = TextEditingController();
    
    return showDialog<String>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(title),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(message),
              const SizedBox(height: 16),
              TextField(
                controller: controller,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: '密码',
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, controller.text),
              child: const Text('确定'),
            ),
          ],
        );
      },
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('账户安全'),
        backgroundColor: AppColors.primary,
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 安全状态卡片
                  AnimatedGradientCard(
                    colors: const [
                      Color(0xFF35BB78), // 索克绿
                      Color(0xFF2DAA6B),
                      Color(0xFF1E9059),
                      Color(0xFF188550),
                    ],
                    borderRadius: BorderRadius.circular(16),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                width: 48,
                                height: 48,
                                decoration: BoxDecoration(
                                  color: Colors.white.withAlpha(40),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(
                                  Icons.shield,
                                  color: Colors.white,
                                  size: 28,
                                ),
                              ),
                              const SizedBox(width: 16),
                              const Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      '账户安全状态',
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    SizedBox(height: 4),
                                    Text(
                                      '定期检查您的安全设置',
                                      style: TextStyle(
                                        color: Colors.white70,
                                        fontSize: 14,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),
                          const Divider(
                            color: Colors.white24,
                          ),
                          const SizedBox(height: 20),
                          
                          // 安全状态项目
                          _buildSecurityStatusItem(
                            icon: Icons.password,
                            title: '密码状态',
                            status: _passwordSecurity != null
                                ? (_passwordSecurity!.isSecure ? '安全' : '需要改进')
                                : '未检查',
                            statusColor: _passwordSecurity != null
                                ? (_passwordSecurity!.isSecure ? Colors.green : Colors.orange)
                                : Colors.grey,
                          ),
                          _buildSecurityStatusItem(
                            icon: Icons.confirmation_number,
                            title: '双因素认证',
                            status: _is2FAEnabled ? '已启用 ($_2FAMethod)' : '未启用',
                            statusColor: _is2FAEnabled ? Colors.green : Colors.orange,
                          ),
                          _buildSecurityStatusItem(
                            icon: Icons.fingerprint,
                            title: '生物识别认证',
                            status: _isBiometricEnabled ? '已启用' : '未启用',
                            statusColor: _isBiometricEnabled ? Colors.green : Colors.orange,
                          ),
                          _buildSecurityStatusItem(
                            icon: Icons.login,
                            title: '可疑登录尝试',
                            status: _suspiciousLogins.isEmpty
                                ? '无'
                                : '${_suspiciousLogins.length}次',
                            statusColor: _suspiciousLogins.isEmpty
                                ? Colors.green
                                : Colors.red,
                            isLast: true,
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // 安全选项
                  const Text(
                    '安全选项',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  _buildSecurityOption(
                    icon: Icons.password,
                    title: '修改密码',
                    subtitle: '定期更改您的密码',
                    onTap: () => context.router.push(const ChangePasswordRoute()),
                  ),
                  
                  _buildSecurityOption(
                    icon: Icons.security_update_good,
                    title: '检查密码安全性',
                    subtitle: '检查您的密码是否足够强壮',
                    onTap: _checkPasswordSecurity,
                  ),
                  
                  _buildSecurityOption(
                    icon: Icons.confirmation_number,
                    title: '双因素认证',
                    subtitle: _is2FAEnabled ? '已启用($_2FAMethod)' : '提高账户安全性',
                    onTap: () => context.router.push(const TwoFactorSettingsRoute()),
                    trailing: Switch(
                      value: _is2FAEnabled,
                      activeColor: AppColors.primary,
                      onChanged: (value) {
                        if (value) {
                          context.router.push(const TwoFactorSettingsRoute());
                        } else {
                          // 显示禁用2FA确认对话框
                          showDialog(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: const Text('禁用双因素认证'),
                              content: const Text('禁用双因素认证将会降低您账户的安全性，确定要继续吗？'),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.of(context).pop(),
                                  child: const Text('取消'),
                                ),
                                TextButton(
                                  onPressed: () async {
                                    Navigator.of(context).pop();
                                    
                                    // 获取验证码
                                    final verificationCode = await _showPasswordPrompt(
                                      context,
                                      '确认验证码',
                                      '请输入您的验证码以禁用双因素认证'
                                    );
                                    
                                    if (verificationCode != null && verificationCode.isNotEmpty) {
                                      setState(() {
                                        _isLoading = true;
                                      });
                                      
                                      try {
                                        final authUseCases = ref.read(authUseCasesProvider);
                                        final result = await authUseCases.disable2FA(verificationCode);
                                        
                                        setState(() {
                                          _is2FAEnabled = !result;
                                          _isLoading = false;
                                        });
                                        
                                        if (result) {
                                          ScaffoldMessenger.of(context).showSnackBar(
                                            const SnackBar(
                                              content: Text('双因素认证已禁用'),
                                              backgroundColor: Colors.green,
                                            ),
                                          );
                                        }
                                      } catch (e) {
                                        setState(() {
                                          _isLoading = false;
                                        });
                                        
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          SnackBar(
                                            content: Text('禁用双因素认证失败: ${e.toString()}'),
                                            backgroundColor: Colors.red,
                                          ),
                                        );
                                      }
                                    }
                                  },
                                  child: const Text('禁用'),
                                ),
                              ],
                            ),
                          );
                        }
                      },
                    ),
                  ),
                  
                  _buildSecurityOption(
                    icon: Icons.recovery_convert,
                    title: '恢复代码',
                    subtitle: '管理账户恢复代码',
                    onTap: () => context.router.push(const RecoveryCodesRoute()),
                  ),
                  
                  _buildSecurityOption(
                    icon: Icons.devices,
                    title: '管理登录会话',
                    subtitle: '查看和控制您的活跃会话',
                    onTap: () => context.router.push(const SessionManagementRoute()),
                  ),
                  
                  if (_suspiciousLogins.isNotEmpty)
                    _buildSecurityOption(
                      icon: Icons.warning,
                      title: '可疑登录尝试',
                      subtitle: '查看可疑的登录活动',
                      onTap: () => context.router.push(SuspiciousLoginsRoute(
                        attempts: _suspiciousLogins,
                      )),
                      isWarning: true,
                    ),
                  
                  const SizedBox(height: 24),
                  
                  // 关联账号
                  const Text(
                    '关联账号',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  _buildSocialAccountItem(
                    icon: 'assets/icons/wechat.svg',
                    title: '微信',
                    isConnected: _linkedAccounts['wechat'] ?? false,
                    onTap: () => _manageSocialAccount('wechat'),
                  ),
                  
                  _buildSocialAccountItem(
                    icon: 'assets/icons/xiaohongshu.svg',
                    title: '小红书',
                    isConnected: _linkedAccounts['xiaohongshu'] ?? false,
                    onTap: () => _manageSocialAccount('xiaohongshu'),
                  ),
                  
                  _buildSocialAccountItem(
                    icon: 'assets/icons/douyin.svg',
                    title: '抖音',
                    isConnected: _linkedAccounts['douyin'] ?? false,
                    onTap: () => _manageSocialAccount('douyin'),
                  ),
                  
                  _buildSocialAccountItem(
                    icon: 'assets/icons/alipay.svg',
                    title: '支付宝',
                    isConnected: _linkedAccounts['alipay'] ?? false,
                    onTap: () => _manageSocialAccount('alipay'),
                  ),
                  
                  const SizedBox(height: 32),
                ],
              ),
            ),
    );
  }
  
  /// 管理社交账号
  void _manageSocialAccount(String provider) {
    final isConnected = _linkedAccounts[provider] ?? false;
    
    if (isConnected) {
      // 解绑账号
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('解绑${_getProviderDisplayName(provider)}'),
          content: Text('确定要解绑您的${_getProviderDisplayName(provider)}账号吗？'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('取消'),
            ),
            TextButton(
              onPressed: () async {
                Navigator.of(context).pop();
                
                setState(() {
                  _isLoading = true;
                });
                
                try {
                  final authUseCases = ref.read(authUseCasesProvider);
                  final result = await authUseCases.unlinkSocialAccount(provider);
                  
                  if (result) {
                    setState(() {
                      _linkedAccounts[provider] = false;
                      _isLoading = false;
                    });
                    
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('${_getProviderDisplayName(provider)}账号已解绑'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  }
                } catch (e) {
                  setState(() {
                    _isLoading = false;
                  });
                  
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('解绑账号失败: ${e.toString()}'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              },
              child: const Text('解绑'),
            ),
          ],
        ),
      );
    } else {
      // 绑定账号
      context.router.push(
        SocialAccountLinkRoute(provider: provider),
      );
    }
  }
  
  /// 获取提供商显示名称
  String _getProviderDisplayName(String provider) {
    switch (provider) {
      case 'wechat':
        return '微信';
      case 'xiaohongshu':
        return '小红书';
      case 'douyin':
        return '抖音';
      case 'alipay':
        return '支付宝';
      default:
        return provider;
    }
  }
  
  /// 构建安全状态项目
  Widget _buildSecurityStatusItem({
    required IconData icon,
    required String title,
    required String status,
    required Color statusColor,
    bool isLast = false,
  }) {
    return Padding(
      padding: EdgeInsets.only(bottom: isLast ? 0 : 16),
      child: Row(
        children: [
          Icon(
            icon,
            size: 20,
            color: Colors.white,
          ),
          const SizedBox(width: 12),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
            ),
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 4,
            ),
            decoration: BoxDecoration(
              color: statusColor.withAlpha(40),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              status,
              style: TextStyle(
                color: statusColor,
                fontWeight: FontWeight.w500,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  /// 构建安全选项
  Widget _buildSecurityOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    Widget? trailing,
    bool isWarning = false,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: isWarning
            ? BorderSide(color: Colors.red.withAlpha(100), width: 1)
            : BorderSide.none,
      ),
      elevation: 1,
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 8,
        ),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: isWarning
                ? Colors.red.withAlpha(30)
                : AppColors.primary.withAlpha(30),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            icon,
            color: isWarning ? Colors.red : AppColors.primary,
          ),
        ),
        title: Text(
          title,
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: isWarning ? Colors.red : Colors.black87,
          ),
        ),
        subtitle: Text(subtitle),
        trailing: trailing ?? const Icon(Icons.chevron_right),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        onTap: onTap,
      ),
    );
  }
  
  /// 构建社交账号项目
  Widget _buildSocialAccountItem({
    required String icon,
    required String title,
    required bool isConnected,
    required VoidCallback onTap,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      elevation: 1,
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 8,
        ),
        leading: SizedBox(
          width: 40,
          height: 40,
          child: Center(
            child: Image.asset(
              icon,
              width: 28,
              height: 28,
            ),
          ),
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.w500,
          ),
        ),
        subtitle: Text(
          isConnected ? '已关联' : '未关联',
          style: TextStyle(
            color: isConnected ? Colors.green : Colors.grey,
          ),
        ),
        trailing: TextButton(
          onPressed: onTap,
          child: Text(isConnected ? '解绑' : '关联'),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        onTap: onTap,
      ),
    );
  }
} 