import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/usecases/auth_usecases.dart';
import 'package:suoke_life/di/providers/auth_providers.dart';
import 'package:suoke_life/core/widgets/animated_gradient_card.dart';
import 'package:suoke_life/core/widgets/animated_press_button.dart';
import 'package:suoke_life/presentation/auth/widgets/session_item.dart';

/// 会话管理页面
class SessionManagementPage extends ConsumerStatefulWidget {
  const SessionManagementPage({Key? key}) : super(key: key);
  
  @override
  ConsumerState<SessionManagementPage> createState() => _SessionManagementPageState();
}

class _SessionManagementPageState extends ConsumerState<SessionManagementPage> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  List<UserSession> _sessions = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    
    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
    
    _loadSessions();
  }
  
  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }
  
  /// 加载会话数据
  Future<void> _loadSessions() async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      final authUseCases = ref.read(authUseCasesProvider);
      final sessions = await authUseCases.getSessions();
      
      setState(() {
        _sessions = sessions;
        _isLoading = false;
      });
      
      _animationController.forward();
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('获取会话数据失败: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  /// 终止会话
  Future<void> _terminateSession(String sessionId) async {
    try {
      setState(() {
        _isLoading = true;
      });
      
      final authUseCases = ref.read(authUseCasesProvider);
      await authUseCases.terminateSession(sessionId);
      
      // 从列表中移除已终止的会话
      setState(() {
        _sessions.removeWhere((session) => session.id == sessionId);
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('会话已成功终止'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('终止会话失败: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  /// 终止所有其他会话
  Future<void> _terminateAllOtherSessions() async {
    try {
      setState(() {
        _isLoading = true;
      });
      
      final authUseCases = ref.read(authUseCasesProvider);
      await authUseCases.terminateAllOtherSessions();
      
      // 仅保留当前会话
      setState(() {
        _sessions = _sessions.where((session) => session.isCurrent).toList();
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('所有其他设备的会话已成功终止'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('终止所有会话失败: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('活跃会话管理'),
        backgroundColor: AppColors.primary,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadSessions,
            tooltip: '刷新会话列表',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
              ),
            )
          : _sessions.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.devices_off,
                        size: 64,
                        color: AppColors.primary.withAlpha(150),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        '没有活跃的会话',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        '您当前没有任何活跃的登录会话',
                        style: TextStyle(
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                )
              : Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(16),
                      child: AnimatedGradientCard(
                        colors: const [
                          Color(0xFF35BB78), // 索克绿
                          Color(0xFF2DAA6B),
                          Color(0xFF1E9059),
                          Color(0xFF188550),
                        ],
                        borderRadius: BorderRadius.circular(12),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  const Icon(
                                    Icons.security,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(width: 8),
                                  const Text(
                                    '账户安全提示',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              const Text(
                                '您目前有 ${_sessions.length} 个活跃会话。请检查列表，确保这些都是您自己的设备。如发现可疑登录，请立即终止并修改密码。',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 14,
                                ),
                              ),
                              const SizedBox(height: 16),
                              AnimatedPressButton(
                                onPressed: _terminateAllOtherSessions,
                                width: double.infinity,
                                height: 44,
                                backgroundColor: Colors.white,
                                foregroundColor: AppColors.primary,
                                splashColor: Colors.grey.withAlpha(80),
                                borderRadius: BorderRadius.circular(8),
                                child: const Text(
                                  '终止所有其他设备的会话',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    Expanded(
                      child: FadeTransition(
                        opacity: _fadeAnimation,
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _sessions.length,
                          itemBuilder: (context, index) {
                            final session = _sessions[index];
                            return SessionItem(
                              session: session,
                              onTerminate: () => _terminateSession(session.id),
                            );
                          },
                        ),
                      ),
                    ),
                  ],
                ),
    );
  }
} 