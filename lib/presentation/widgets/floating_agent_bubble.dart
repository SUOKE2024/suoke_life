import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/domain/models/voice_state.dart';
import 'package:suoke_life/domain/services/voice_service.dart';
import 'package:suoke_life/presentation/suoke/view_models/agent_view_model.dart';
import 'package:suoke_life/di/providers.dart';

/// 浮动智能体气泡组件
class FloatingAgentBubble extends ConsumerStatefulWidget {
  /// 智能体类型
  final AgentType agentType;
  
  /// 服务场景
  final String scene;
  
  /// 服务提示消息
  final String promptMessage;
  
  /// 显示延迟（毫秒）
  final int showDelay;
  
  /// 气泡位置
  final BubblePosition position;
  
  /// 构造函数
  const FloatingAgentBubble({
    Key? key,
    required this.agentType,
    required this.scene,
    required this.promptMessage,
    this.showDelay = 1500,
    this.position = BubblePosition.bottomRight,
  }) : super(key: key);

  @override
  ConsumerState<FloatingAgentBubble> createState() => _FloatingAgentBubbleState();
}

/// 气泡位置枚举
enum BubblePosition {
  /// 左上角
  topLeft,
  
  /// 右上角
  topRight,
  
  /// 左下角
  bottomLeft,
  
  /// 右下角
  bottomRight,
}

/// 交互模式枚举
enum InteractionMode {
  /// 语音模式
  voice,
  
  /// 文本模式
  text,
  
  /// 收起状态
  collapsed,
  
  /// 隐藏状态
  hidden,
}

class _FloatingAgentBubbleState extends ConsumerState<FloatingAgentBubble> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _opacityAnimation;
  late Animation<double> _slideAnimation;
  bool _isVisible = false;
  bool _isExpanded = false;
  InteractionMode _interactionMode = InteractionMode.collapsed;
  final TextEditingController _textController = TextEditingController();
  bool _isListening = false;
  String _voiceRecognitionText = '';
  
  // 手势拖动相关
  Offset _dragOffset = Offset.zero;
  bool _isDragging = false;
  
  @override
  void initState() {
    super.initState();
    
    // 初始化动画控制器
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    
    // 缩放动画
    _scaleAnimation = Tween<double>(begin: 0.3, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.elasticOut),
    );
    
    // 透明度动画
    _opacityAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeIn),
    );
    
    // 滑动动画
    _slideAnimation = Tween<double>(begin: 100.0, end: 0.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOutQuart),
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
    _textController.dispose();
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
    
    // 根据位置设置对齐方式
    final Alignment alignment = _getPositionAlignment();
    
    return Align(
      alignment: alignment,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: GestureDetector(
          onPanStart: (details) {
            setState(() {
              _isDragging = true;
            });
          },
          onPanUpdate: (details) {
            setState(() {
              _dragOffset += details.delta;
            });
          },
          onPanEnd: (details) {
            setState(() {
              _isDragging = false;
            });
          },
          child: AnimatedBuilder(
            animation: _animationController,
            builder: (context, child) {
              return Opacity(
                opacity: _opacityAnimation.value,
                child: Transform.translate(
                  offset: Offset(
                    _slideAnimation.value * (widget.position == BubblePosition.topLeft || widget.position == BubblePosition.bottomLeft ? -1 : 1),
                    _slideAnimation.value * (widget.position == BubblePosition.topLeft || widget.position == BubblePosition.topRight ? -1 : 1),
                  ),
                  child: Transform.scale(
                    scale: _scaleAnimation.value,
                    child: child,
                  ),
                ),
              );
            },
            child: _interactionMode == InteractionMode.collapsed
                ? _buildCollapsedBubble(agent)
                : _buildExpandedBubble(agent),
          ),
        ),
      ),
    );
  }
  
  /// 构建收起状态的气泡
  Widget _buildCollapsedBubble(Agent agent) {
    return GestureDetector(
      onTap: _toggleExpanded,
      child: Container(
        width: 60,
        height: 60,
        decoration: BoxDecoration(
          color: agent.themeColor,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Center(
          child: CircleAvatar(
            radius: 24,
            backgroundColor: agent.themeColor.withOpacity(0.2),
            child: Icon(
              _getAgentIcon(agent.type),
              color: agent.themeColor,
              size: 32,
            ),
          ),
        ),
      ),
    );
  }
  
  /// 构建展开状态的气泡
  Widget _buildExpandedBubble(Agent agent) {
    return Container(
      width: 300,
      constraints: const BoxConstraints(maxWidth: 300),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 头部
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: agent.themeColor.withOpacity(0.1),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 18,
                  backgroundColor: agent.themeColor.withOpacity(0.2),
                  child: Icon(
                    _getAgentIcon(agent.type),
                    color: agent.themeColor,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  agent.name,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: agent.themeColor,
                    fontSize: 16,
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.keyboard),
                  onPressed: _toggleInteractionMode,
                  color: agent.themeColor,
                  iconSize: 20,
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: _toggleExpanded,
                  color: Colors.grey[600],
                  iconSize: 20,
                ),
              ],
            ),
          ),
          
          // 内容区域
          Container(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _interactionMode == InteractionMode.voice
                      ? '${agent.name}正在听您说话...'
                      : widget.promptMessage,
                  style: TextStyle(
                    color: Colors.grey[800],
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 8),
                if (_interactionMode == InteractionMode.voice && _voiceRecognitionText.isNotEmpty)
                  Text(
                    _voiceRecognitionText,
                    style: const TextStyle(
                      color: Colors.black,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                if (_interactionMode == InteractionMode.text)
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _textController,
                          decoration: InputDecoration(
                            hintText: '请输入您的问题...',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(20),
                              borderSide: BorderSide.none,
                            ),
                            filled: true,
                            fillColor: Colors.grey[100],
                            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          ),
                          onSubmitted: (text) => _sendMessage(text),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.send),
                        onPressed: () => _sendMessage(_textController.text),
                        color: agent.themeColor,
                      ),
                    ],
                  ),
                
                // 按钮区域
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    if (_interactionMode == InteractionMode.voice)
                      InkWell(
                        onTap: _toggleVoiceRecognition,
                        child: Container(
                          width: 60,
                          height: 60,
                          decoration: BoxDecoration(
                            color: _isListening ? agent.themeColor : Colors.grey[200],
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            _isListening ? Icons.mic : Icons.mic_none,
                            color: _isListening ? Colors.white : Colors.grey[700],
                            size: 30,
                          ),
                        ),
                      ),
                    
                    ElevatedButton(
                      onPressed: _startChat,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: agent.themeColor,
                        foregroundColor: Colors.white,
                        minimumSize: const Size(100, 40),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20),
                        ),
                      ),
                      child: const Text('开始对话'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  /// 切换展开状态
  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
      if (_isExpanded) {
        _interactionMode = InteractionMode.voice; // 默认展开为语音模式
      } else {
        _interactionMode = InteractionMode.collapsed;
      }
    });
  }
  
  /// 切换交互模式
  void _toggleInteractionMode() {
    setState(() {
      if (_interactionMode == InteractionMode.voice) {
        _interactionMode = InteractionMode.text;
      } else {
        _interactionMode = InteractionMode.voice;
      }
    });
  }
  
  /// 切换语音识别状态
  void _toggleVoiceRecognition() {
    final voiceService = ref.read(voiceServiceProvider);
    
    setState(() {
      _isListening = !_isListening;
      if (_isListening) {
        _voiceRecognitionText = ''; // 清空之前的识别文本
        
        // 使用语音服务模拟语音识别
        _simulateRealVoiceRecognition();
      } else {
        // 停止语音识别
        voiceService.stopListening();
      }
    });
  }
  
  /// 使用语音服务模拟语音识别
  void _simulateRealVoiceRecognition() {
    final voiceService = ref.read(voiceServiceProvider);
    
    // 直接模拟语音识别过程，不依赖具体实现类
    voiceService.startListening().then((_) {
      // 手动模拟识别过程
      Future.delayed(const Duration(seconds: 1), () {
        if (mounted) {
          setState(() {
            _voiceRecognitionText = '我想了解';
          });
          
          Future.delayed(const Duration(milliseconds: 500), () {
            if (mounted) {
              setState(() {
                _voiceRecognitionText = '我想了解一下中医体质';
              });
              
              Future.delayed(const Duration(milliseconds: 700), () {
                if (mounted) {
                  setState(() {
                    _voiceRecognitionText = '我想了解一下中医体质检测的方法';
                    _isListening = false; // 自动停止录音
                  });
                  
                  // 停止语音识别
                  voiceService.stopListening();
                  
                  // 识别完成后延迟一会儿发送消息
                  Future.delayed(const Duration(milliseconds: 800), () {
                    if (mounted && _voiceRecognitionText.isNotEmpty) {
                      _sendMessage(_voiceRecognitionText);
                    }
                  });
                }
              });
            }
          });
        }
      });
    });
  }
  
  /// 发送消息
  void _sendMessage(String text) {
    if (text.trim().isEmpty) return;
    
    final viewModel = ref.read(agentViewModelProvider.notifier);
    
    // 关闭气泡
    _animationController.reverse().then((_) {
      if (mounted) {
        setState(() {
          _isVisible = false;
        });
      }
    });
    
    // 切换到对应智能体
    viewModel.switchAgent(widget.agentType).then((_) {
      // 创建新对话
      viewModel.createNewConversation(title: '关于${widget.scene}的对话').then((_) {
        // 导航到聊天页面
        Navigator.pushNamed(context, '/chat');
        
        // 发送系统消息和用户消息
        Future.delayed(const Duration(milliseconds: 300), () {
          viewModel.sendSystemMessage(
            "用户从${widget.scene}场景进入对话，请提供相关服务。",
            hidden: true,
          ).then((_) {
            // 发送用户消息
            viewModel.sendMessage(text);
          });
        });
      });
    });
    
    // 清空文本框
    _textController.clear();
  }
  
  /// 开始聊天（不发送特定内容）
  void _startChat() {
    final viewModel = ref.read(agentViewModelProvider.notifier);
    
    // 关闭气泡
    _animationController.reverse().then((_) {
      if (mounted) {
        setState(() {
          _isVisible = false;
        });
      }
    });
    
    // 切换到对应智能体
    viewModel.switchAgent(widget.agentType).then((_) {
      // 创建新对话
      viewModel.createNewConversation(title: '关于${widget.scene}的对话').then((_) {
        // 导航到聊天页面
        Navigator.pushNamed(context, '/chat');
        
        // 发送系统消息
        Future.delayed(const Duration(milliseconds: 300), () {
          viewModel.sendSystemMessage(
            "用户从${widget.scene}场景进入对话，请提供相关服务。",
            hidden: true,
          );
        });
      });
    });
  }
  
  /// 根据位置获取对齐方式
  Alignment _getPositionAlignment() {
    switch (widget.position) {
      case BubblePosition.topLeft:
        return Alignment.topLeft;
      case BubblePosition.topRight:
        return Alignment.topRight;
      case BubblePosition.bottomLeft:
        return Alignment.bottomLeft;
      case BubblePosition.bottomRight:
        return Alignment.bottomRight;
    }
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
  
  /// 获取智能体图标
  IconData _getAgentIcon(AgentType type) {
    switch (type) {
      case AgentType.xiaoAi:
        return Icons.assistant;
      case AgentType.xiaoKe:
        return Icons.shopping_cart;
      case AgentType.laoKe:
        return Icons.school;
      case AgentType.suoEr:
        return Icons.favorite;
    }
  }
} 