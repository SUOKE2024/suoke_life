import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/presentation/suoke/view_models/agent_view_model.dart';
import 'package:suoke_life/di/providers.dart';

/// 智能体主动服务组件
class ProactiveAgentService extends ConsumerStatefulWidget {
  /// 智能体类型
  final AgentType agentType;
  
  /// 服务场景
  final String scene;
  
  /// 服务提示消息
  final String promptMessage;
  
  /// 显示延迟（毫秒）
  final int showDelay;
  
  /// 构造函数
  const ProactiveAgentService({
    Key? key,
    required this.agentType,
    required this.scene,
    required this.promptMessage,
    this.showDelay = 2000,
  }) : super(key: key);

  @override
  ConsumerState<ProactiveAgentService> createState() => _ProactiveAgentServiceState();
}

class _ProactiveAgentServiceState extends ConsumerState<ProactiveAgentService> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _opacityAnimation;
  bool _isVisible = false;
  
  @override
  void initState() {
    super.initState();
    
    // 初始化动画控制器
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    
    // 缩放动画
    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOutBack),
    );
    
    // 透明度动画
    _opacityAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeIn),
    );
    
    // 延迟显示
    Future.delayed(Duration(milliseconds: widget.showDelay), () {
      if (mounted) {
        setState(() {
          _isVisible = true;
        });
        _animationController.forward();
      }
    });
  }
  
  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isVisible) {
      return const SizedBox.shrink();
    }
    
    final agentState = ref.watch(agentViewModelProvider);
    
    // 获取对应类型的智能体
    final agent = agentState.agents.firstWhere(
      (a) => a.type == widget.agentType,
      orElse: () => Agent(
        id: 'default',
        name: _getAgentName(widget.agentType),
        type: widget.agentType,
        description: '',
        avatarUrl: _getAgentAvatar(widget.agentType),
        lastActiveTime: DateTime.now(),
        createdAt: DateTime.now(),
      ),
    );
    
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return Opacity(
          opacity: _opacityAnimation.value,
          child: Transform.scale(
            scale: _scaleAnimation.value,
            child: child,
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.all(16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
          border: Border.all(
            color: agent.themeColor.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Row(
          children: [
            // 智能体头像
            CircleAvatar(
              radius: 24,
              backgroundImage: AssetImage(agent.avatarUrl),
            ),
            const SizedBox(width: 12),
            
            // 消息内容
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    agent.name,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: agent.themeColor,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.promptMessage,
                    style: TextStyle(
                      color: Colors.grey[800],
                    ),
                  ),
                ],
              ),
            ),
            
            // 按钮
            Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () {
                    _animationController.reverse().then((_) {
                      if (mounted) {
                        setState(() {
                          _isVisible = false;
                        });
                      }
                    });
                  },
                  iconSize: 18,
                  color: Colors.grey,
                ),
                const SizedBox(height: 4),
                ElevatedButton(
                  onPressed: _startChat,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: agent.themeColor,
                    foregroundColor: Colors.white,
                    minimumSize: const Size(80, 36),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(18),
                    ),
                  ),
                  child: const Text('开始'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  /// 开始聊天
  void _startChat() {
    final viewModel = ref.read(agentViewModelProvider.notifier);
    
    // 切换到对应智能体
    viewModel.switchAgent(widget.agentType).then((_) {
      // 创建新对话
      viewModel.createNewConversation(title: '关于${widget.scene}的对话').then((_) {
        // 导航到聊天页面
        Navigator.pushNamed(context, '/chat');
        
        // 发送初始消息
        Future.delayed(const Duration(milliseconds: 500), () {
          viewModel.sendSystemMessage(
            "用户从${widget.scene}场景进入对话，请提供相关服务。",
            hidden: true,
          );
        });
      });
    });
    
    setState(() {
      _isVisible = false;
    });
  }
  
  /// 获取智能体名称
  String _getAgentName(AgentType type) {
    switch (type) {
      case AgentType.xiaoAi:
        return '小艾';
      case AgentType.xiaoKe:
        return '小克';
      case AgentType.laoKe:
        return '老克';
      case AgentType.suoEr:
        return '索儿';
    }
  }
  
  /// 获取智能体头像
  String _getAgentAvatar(AgentType type) {
    switch (type) {
      case AgentType.xiaoAi:
        return 'assets/images/avatars/xiaoai.png';
      case AgentType.xiaoKe:
        return 'assets/images/avatars/xiaoke.png';
      case AgentType.laoKe:
        return 'assets/images/avatars/laoke.png';
      case AgentType.suoEr:
        return 'assets/images/avatars/suoer.png';
    }
  }
} 