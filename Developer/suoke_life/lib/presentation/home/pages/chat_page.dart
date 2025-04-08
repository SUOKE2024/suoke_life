import 'package:flutter/material.dart';
import 'dart:ui';
import 'dart:math' as math;
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/utils/permission_utils.dart';
import 'package:suoke_life/core/services/speech_service.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:permission_handler/permission_handler.dart' as ph;
import 'package:suoke_life/core/services/deepseek_service.dart';
import 'package:suoke_life/core/services/multimodal_data_service.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/widgets/tcm/models/tongue_diagnosis_data.dart';
import 'package:suoke_life/core/config/app_config.dart';

/// 聊天页面 - 显示与某个联系人的聊天内容
@RoutePage()
class ChatPage extends ConsumerStatefulWidget {
  final String contactName;
  final String contactAvatar; // 暂时仅作为标识符使用，不实际加载图片
  final bool isAI;

  const ChatPage({
    super.key,
    required this.contactName,
    required this.contactAvatar,
    this.isAI = false,
  });

  @override
  ConsumerState<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends ConsumerState<ChatPage> {
  // 消息记录
  final List<Map<String, dynamic>> _messages = [
    {
      'sender': 'ai',
      'content': '你好！我是索克AI助手，专注于中医养生和健康生活方式指导。有什么我可以帮助你的吗？',
      'timestamp': DateTime.now().subtract(const Duration(days: 1)),
      'isRead': true,
    },
    {
      'sender': 'user',
      'content': '我最近睡眠质量不太好，有什么改善方法吗？',
      'timestamp': DateTime.now().subtract(const Duration(minutes: 45)),
      'isRead': true,
    },
    {
      'sender': 'ai',
      'content':
          '睡眠问题可能与多种因素有关。从中医角度看，可能是心脾两虚或肝郁化火导致。建议：\n\n1. 保持规律作息，晚上11点前入睡\n2. 睡前泡脚，水温40-45度，15-20分钟\n3. 避免睡前使用电子产品\n4. 可以尝试睡前喝一杯温牛奶或蜂蜜水\n5. 白天适当运动，但避免晚上剧烈运动\n\n需要更详细的建议，可以告诉我你的具体症状。',
      'timestamp': DateTime.now().subtract(const Duration(minutes: 43)),
      'isRead': true,
    },
    {
      'sender': 'user',
      'content': '谢谢建议，我会试试看。对了，最近是什么节气？有什么养生建议吗？',
      'timestamp': DateTime.now().subtract(const Duration(minutes: 30)),
      'isRead': true,
    },
    {
      'sender': 'ai',
      'content':
          '现在是谷雨节气(4月20日左右)，是春季最后一个节气，雨水增多，万物生长。\n\n谷雨养生建议：\n\n1. 饮食：宜清淡，可适当食用春笋、荠菜、菠菜等时令蔬菜，帮助肝脏排毒\n\n2. 起居：早睡早起，保持充足睡眠\n\n3. 运动：可进行舒缓运动如太极、瑜伽，增强身体阳气\n\n4. 情志：保持心情舒畅，避免情绪波动\n\n5. 穴位按摩：按摩足三里、阳陵泉等穴位，促进气血循环\n\n要了解更多养生信息，可以查看LIFE频道的节气养生专栏。',
      'timestamp': DateTime.now().subtract(const Duration(minutes: 28)),
      'isRead': true,
    },
  ];

  // 热门话题
  final List<String> _hotTopics = [
    '睡眠质量提升',
    '春季养肝食谱',
    '颈椎保健指南',
    '提高免疫力',
    '舒缓压力方法',
    '四季养生咖啡',
    '中医体质辨识',
  ];

  // 文本编辑控制器
  final TextEditingController _messageController = TextEditingController();
  // 滚动控制器
  final ScrollController _scrollController = ScrollController();

  // 麦克风状态
  bool _isMicrophoneOn = false;

  // 电话通话状态
  bool _isCallActive = false;

  // 主动语音回复状态 - 默认打开
  bool _autoVoiceReply = true;

  // 语音权限状态
  bool _hasRequestedPermission = false;

  // 背景图片路径
  String? _backgroundImage;

  // 当前会话ID
  late String _sessionId;

  // 当前选择的图片路径
  String? _selectedImagePath;

  // 是否正在处理请求
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    // 创建新的会话ID
    _sessionId = MultimodalDataService.createSessionId();

    // 收集初始消息
    _collectInitialMessages();

    // 延迟执行，等待页面完全加载
    Future.delayed(const Duration(seconds: 1), () async {
      // 添加欢迎消息
      _addWelcomeMessage();

      // 直接检查麦克风权限状态
      _checkMicPermissionInBackground();
    });
  }

  /// 在后台检查麦克风权限状态，不显示对话框
  Future<void> _checkMicPermissionInBackground() async {
    try {
      final status = await ph.Permission.microphone.status;

      if (status.isGranted) {
        // 已授权，自动开启语音
        _autoActivateVoiceInteraction();
      } else {
        // 未授权，仅在界面增加提示，不弹出对话框
        setState(() {
          _messages.add({
            'sender': 'ai',
            'content': '要体验语音交互功能，请点击右上角的麦克风图标并授予权限。您随时可以通过语音与我交流，让沟通更加便捷。',
            'timestamp': DateTime.now().add(const Duration(seconds: 1)),
            'isRead': true,
          });
        });
      }
    } catch (e) {
      debugPrint('后台检查麦克风权限出错: $e');
    }
  }

  /// 点击麦克风按钮时简化的权限请求流程
  void _toggleMicrophone() async {
    try {
      final speechService = ref.read(speechServiceProvider.notifier);

      if (_isMicrophoneOn) {
        // 如果麦克风已开启，则关闭
        await speechService.stopListening();
        setState(() {
          _isMicrophoneOn = false;
        });

        // 提示用户
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('语音识别已暂停'),
            duration: Duration(seconds: 1),
            behavior: SnackBarBehavior.floating,
          ),
        );
        return;
      }

      // 如果通话不处于活跃状态，先启动通话
      if (!_isCallActive) {
        setState(() {
          _isCallActive = true;
        });
      }

      // 尝试请求麦克风权限
      final status = await ph.Permission.microphone.request();

      if (status.isGranted) {
        // 权限已授予，开启麦克风
        setState(() {
          _isMicrophoneOn = true;
          _hasRequestedPermission = true;
        });

        // 开始语音识别
        _startVoiceRecognition();

        // 成功反馈
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('麦克风已开启，请开始说话'),
            duration: Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      } else if (status.isPermanentlyDenied) {
        // 用户永久拒绝了权限，需要到设置中开启
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('请在设备设置中手动授予麦克风权限'),
            duration: const Duration(seconds: 3),
            behavior: SnackBarBehavior.floating,
            action: SnackBarAction(
              label: '打开设置',
              onPressed: () {
                PermissionUtils.openAppSettings();
              },
            ),
          ),
        );
      } else {
        // 用户拒绝了权限，但可以再次请求
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('需要麦克风权限才能使用语音功能'),
            duration: Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      debugPrint('麦克风切换失败: $e');
      // 发生异常，重置状态
      setState(() {
        _isMicrophoneOn = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('麦克风操作失败，请稍后再试'),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    }
  }

  /// 自动激活语音交互
  Future<void> _autoActivateVoiceInteraction() async {
    try {
      // 检查权限前先将状态标记为已请求，避免重复请求
      _hasRequestedPermission = true;

      // 首先检查语音服务状态
      final speechService = ref.read(speechServiceProvider.notifier);
      final currentState = ref.read(speechServiceProvider);

      debugPrint('自动激活语音交互 - 当前语音服务状态: $currentState');

      // 如果服务处于错误状态，尝试重新初始化
      if (currentState == SpeechRecognitionStatus.error) {
        debugPrint('语音服务处于错误状态，尝试强制重新初始化');
        await speechService.forceReInitialize();
        // 短暂延迟，等待初始化完成
        await Future.delayed(const Duration(milliseconds: 500));
      }

      // 请求麦克风权限
      final hasPermission = await PermissionUtils.requestMicrophonePermission();

      if (hasPermission) {
        debugPrint('已获得麦克风权限，尝试激活语音交互');

        // 如果已获得权限，自动开启语音通话
        setState(() {
          _isCallActive = true;
          _isMicrophoneOn = true;
        });

        // 确保更新UI后再开启语音识别
        await Future.delayed(const Duration(milliseconds: 300));

        // 开启语音识别 - 不使用await，因为_startVoiceRecognition内部有自己的异步处理
        _startVoiceRecognition();

        // 提示用户语音已激活
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('语音交互已自动激活，您可以直接对我说话'),
              duration: Duration(seconds: 3),
              behavior: SnackBarBehavior.floating,
            ),
          );
        }
      } else {
        debugPrint('未获得麦克风权限，无法自动激活语音交互');

        // 如果未获得权限，不做任何处理，用户需主动点击麦克风按钮
      }
    } catch (e) {
      debugPrint('自动激活语音交互失败: $e');
      // 出错时不显示任何提示，避免影响用户体验
    }
  }

  /// 请求麦克风权限的明确操作
  void _requestMicPermissionManually() async {
    try {
      // 标记已请求权限，避免重复请求
      setState(() {
        _hasRequestedPermission = true;
      });

      // 显示请求中提示
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('正在请求麦克风权限...'),
            duration: Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }

      // 安全获取语音服务
      final speechService = ref.read(speechServiceProvider.notifier);

      // 确保停止任何正在进行的语音识别
      try {
        await speechService.stopListening();
      } catch (e) {
        debugPrint('停止语音识别失败: $e');
        // 继续执行，不影响后续流程
      }

      // 使用非阻塞方式添加权限请求提示消息
      Future.microtask(() {
        if (mounted) {
          setState(() {
            _messages.add({
              'sender': 'ai',
              'content': '需要麦克风权限才能使用语音对话功能。请在弹出的权限请求对话框中选择"允许"。',
              'timestamp': DateTime.now(),
              'isRead': true,
            });
          });
        }
      });

      // 等待UI更新
      await Future.delayed(const Duration(milliseconds: 300));

      // 使用单独的异步操作请求权限
      bool permissionGranted = false;
      try {
        // 请求权限
        final status = await ph.Permission.microphone.request();
        permissionGranted = status.isGranted;
        debugPrint('麦克风权限请求结果: $status');
      } catch (e) {
        debugPrint('请求麦克风权限异常: $e');
        permissionGranted = false;
      }

      // 确保UI更新和用户体验不受权限结果影响
      if (!mounted) return;

      // 根据权限结果执行不同操作
      if (permissionGranted) {
        // 权限授予成功，更新状态
        setState(() {
          _isCallActive = true;
          _isMicrophoneOn = true;
        });

        // 添加成功消息
        setState(() {
          _messages.add({
            'sender': 'ai',
            'content': '太好了！麦克风权限已获取，您现在可以直接对我说话了。',
            'timestamp': DateTime.now(),
            'isRead': true,
          });
        });

        // 显示提示
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('麦克风权限已获取，语音对话已启动'),
            duration: Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );

        // 延迟启动语音识别，避免状态更新冲突
        Future.delayed(const Duration(milliseconds: 500), () {
          if (mounted) {
            _startVoiceRecognition();
          }
        });
      } else {
        // 权限获取失败
        setState(() {
          _messages.add({
            'sender': 'ai',
            'content':
                '看起来没有获得麦克风权限。您可以在设备设置 > 隐私与安全 > 麦克风 中找到本应用并手动授予权限，然后重新点击麦克风图标。',
            'timestamp': DateTime.now(),
            'isRead': true,
          });
        });

        // 延迟显示提示，确保不与其他UI操作冲突
        Future.delayed(const Duration(milliseconds: 300), () {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: const Text('无法获取麦克风权限，请在设备设置中手动授予权限'),
                duration: const Duration(seconds: 3),
                behavior: SnackBarBehavior.floating,
                action: SnackBarAction(
                  label: '打开设置',
                  onPressed: () async {
                    await PermissionUtils.openAppSettings();
                  },
                ),
              ),
            );
          }
        });
      }
    } catch (e) {
      debugPrint('手动请求麦克风权限失败: $e');

      // 确保UI更新和异常不影响用户体验
      if (mounted) {
        // 显示错误消息
        setState(() {
          _messages.add({
            'sender': 'ai',
            'content': '请求权限时发生错误，请稍后再试。',
            'timestamp': DateTime.now(),
            'isRead': true,
          });
        });

        // 显示错误提示
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
                '权限请求出错: ${e.toString().substring(0, math.min(50, e.toString().length))}...'),
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  /// 收集初始消息数据
  Future<void> _collectInitialMessages() async {
    final multimodalService = ref.read(multimodalDataServiceProvider);

    // 收集AI的初始消息
    for (final message in _messages) {
      if (message['sender'] == 'ai') {
        await multimodalService.collectTextData(
          _sessionId,
          message['content'],
          label: 'ai_initial',
        );
      } else if (message['sender'] == 'user') {
        await multimodalService.collectTextData(
          _sessionId,
          message['content'],
          label: 'user_initial',
        );
      }
    }
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: Stack(
        children: [
          // 背景装饰
          _buildBackground(),

          // 主内容
          SafeArea(
            child: Column(
              children: [
                // 顶部导航栏
                _buildAppBar(),

                // 消息列表
                Expanded(
                  child: _buildMessageList(),
                ),

                // 热门话题（移到底部）
                _buildHotTopics(),

                // 输入框
                _buildMessageInput(),

                // 语音识别状态提示（仅在麦克风开启时显示）
                if (_isMicrophoneOn) _buildVoiceIndicator(),
              ],
            ),
          ),

          // 语音交互状态浮动指示器 (始终显示在左下角，但仅在语音活跃时可见)
          if (_isCallActive)
            Positioned(
              left: 16,
              bottom: 100,
              child: _buildFloatingVoiceIndicator(),
            ),
        ],
      ),
    );
  }

  /// 构建背景装饰
  Widget _buildBackground() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Stack(
      children: [
        // 顶部装饰圆形
        Positioned(
          top: -100,
          right: -100,
          child: Container(
            width: 300,
            height: 300,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.primaryColor.withAlpha(isDarkMode ? 50 : 30),
            ),
          ),
        ),

        // 底部装饰圆形
        Positioned(
          bottom: -150,
          left: -80,
          child: Container(
            width: 350,
            height: 350,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.secondaryColor.withAlpha(isDarkMode ? 50 : 30),
            ),
          ),
        ),
      ],
    );
  }

  /// 构建自定义导航栏
  Widget _buildAppBar() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              // 返回按钮
              _buildAppBarButton(
                Icons.arrow_back,
                () => context.router.pop(),
              ),

              const SizedBox(width: 16),

              // 联系人头像
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: widget.isAI
                      ? AppColors.primaryColor.withAlpha(40)
                      : AppColors.secondaryColor.withAlpha(40),
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withAlpha(15),
                      blurRadius: 5,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Center(
                  child: Icon(
                    widget.isAI ? Icons.psychology : Icons.person,
                    color: widget.isAI
                        ? AppColors.primaryColor
                        : AppColors.secondaryColor,
                    size: 24,
                  ),
                ),
              ),

              const SizedBox(width: 12),

              // 联系人名称
              Text(
                widget.contactName,
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: isDarkMode
                      ? AppColors.darkTextPrimary
                      : AppColors.lightTextPrimary,
                ),
              ),
            ],
          ),
          Row(
            children: [
              // 电话按钮（语音交互）- 用于开始/结束通话
              _buildCallButton(),

              const SizedBox(width: 12),

              // 麦克风按钮（静音控制）
              _buildMicButton(),

              const SizedBox(width: 12),

              // 3点按钮（AI代理设置）
              _buildAppBarButton(
                Icons.more_vert,
                _showAIAgentSettings,
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// 构建导航栏按钮
  Widget _buildAppBarButton(IconData icon, VoidCallback onTap) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    // 为麦克风按钮添加激活状态
    final bool isActiveMic = icon == Icons.mic && _isMicrophoneOn;
    final bool isInactiveMic = icon == Icons.mic_off && !_isMicrophoneOn;

    // 计算按钮颜色 - 麦克风激活状态使用主色调
    final buttonColor = (isActiveMic || isInactiveMic)
        ? AppColors.primaryColor
        : (isDarkMode ? AppColors.darkTextPrimary : AppColors.lightTextPrimary);

    // 计算背景色 - 麦克风激活状态使用半透明主色调背景
    final backgroundColor = isActiveMic
        ? AppColors.primaryColor.withAlpha(30)
        : (isDarkMode ? Colors.white : Colors.black).withAlpha(15);

    return GestureDetector(
      onTap: onTap,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: backgroundColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: (isDarkMode ? Colors.white : Colors.black).withAlpha(30),
                width: 0.5,
              ),
            ),
            child: Icon(
              icon,
              size: 22,
              color: buttonColor,
            ),
          ),
        ),
      ),
    );
  }

  /// 构建热门话题
  Widget _buildHotTopics() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      height: 34, // 原高度是50，缩小三分之一
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _hotTopics.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: GestureDetector(
              onTap: () => _handleHotTopicSend(_hotTopics[index]),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(17), // 高度为34，半径为17
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12, // 水平内边距也相应减小
                      vertical: 6, // 垂直内边距也相应减小
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.primaryColor
                          .withAlpha(isDarkMode ? 40 : 30),
                      borderRadius: BorderRadius.circular(17),
                      border: Border.all(
                        color: AppColors.primaryColor
                            .withAlpha(isDarkMode ? 80 : 60),
                        width: 0.5,
                      ),
                    ),
                    child: Text(
                      _hotTopics[index],
                      style: TextStyle(
                        color: isDarkMode
                            ? AppColors.darkTextPrimary
                            : AppColors.primaryColor.withAlpha(230),
                        fontWeight: FontWeight.bold,
                        fontSize: 11, // 字体也略微缩小
                      ),
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  /// 处理热门话题点击 - 直接发送
  void _handleHotTopicSend(String topic) {
    // 直接使用话题内容作为消息发送
    _messageController.text = topic;
    _handleMessageSend();
  }

  /// 构建消息列表
  Widget _buildMessageList() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });

    return GestureDetector(
      // 添加手势检测器，点击时收起键盘
      onTap: () => FocusScope.of(context).unfocus(),
      child: ListView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(16),
        itemCount: _messages.length,
        itemBuilder: (context, index) {
          final message = _messages[index];
          final bool isUserMessage = message['sender'] == 'user';

          return _buildMessageItem(
            content: message['content'],
            isUserMessage: isUserMessage,
            timestamp: message['timestamp'],
          );
        },
      ),
    );
  }

  /// 构建消息项
  Widget _buildMessageItem({
    required String content,
    required bool isUserMessage,
    required DateTime timestamp,
  }) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment:
            isUserMessage ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUserMessage) _buildAvatar(isUserMessage),
          const SizedBox(width: 8),
          Flexible(
            child: Column(
              crossAxisAlignment: isUserMessage
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(16).copyWith(
                    topLeft: isUserMessage
                        ? const Radius.circular(16)
                        : const Radius.circular(4),
                    topRight: isUserMessage
                        ? const Radius.circular(4)
                        : const Radius.circular(16),
                  ),
                  child: BackdropFilter(
                    filter: ImageFilter.blur(
                        sigmaX: isUserMessage ? 0 : 5,
                        sigmaY: isUserMessage ? 0 : 5),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: isUserMessage
                            ? AppColors.primaryColor
                            : (isDarkMode
                                ? Colors.grey.shade800.withAlpha(160)
                                : Colors.grey.shade100.withAlpha(180)),
                        borderRadius: BorderRadius.circular(16).copyWith(
                          topLeft: isUserMessage
                              ? const Radius.circular(16)
                              : const Radius.circular(4),
                          topRight: isUserMessage
                              ? const Radius.circular(4)
                              : const Radius.circular(16),
                        ),
                        border: !isUserMessage
                            ? Border.all(
                                color: isDarkMode
                                    ? Colors.white.withAlpha(20)
                                    : Colors.white.withAlpha(100),
                                width: 0.5,
                              )
                            : null,
                      ),
                      child: Text(
                        content,
                        style: TextStyle(
                          color: isUserMessage
                              ? Colors.white
                              : (isDarkMode
                                  ? AppColors.darkTextPrimary
                                  : AppColors.lightTextPrimary),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatTimestamp(timestamp),
                  style: TextStyle(
                    fontSize: 10,
                    color: Colors.grey.withAlpha(180),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          if (isUserMessage) _buildAvatar(isUserMessage),
        ],
      ),
    );
  }

  /// 构建头像
  Widget _buildAvatar(bool isUserMessage) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      width: 36,
      height: 36,
      decoration: BoxDecoration(
        color: isUserMessage
            ? AppColors.secondaryColor.withAlpha(40)
            : AppColors.primaryColor.withAlpha(40),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: isDarkMode
                ? Colors.black.withAlpha(30)
                : Colors.black.withAlpha(15),
            blurRadius: 5,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Center(
        child: Icon(
          isUserMessage ? Icons.person : Icons.psychology,
          color:
              isUserMessage ? AppColors.secondaryColor : AppColors.primaryColor,
          size: 20,
        ),
      ),
    );
  }

  /// 格式化时间戳
  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final messageDate =
        DateTime(timestamp.year, timestamp.month, timestamp.day);

    if (messageDate == today) {
      // 今天
      return '今天 ${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}';
    } else if (messageDate == today.subtract(const Duration(days: 1))) {
      // 昨天
      return '昨天 ${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}';
    } else {
      // 其他日期
      return '${timestamp.month}月${timestamp.day}日 ${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}';
    }
  }

  /// 获取系统提示词
  String _getSystemPrompt() {
    return '''你是索克生活APP的AI助手，专注于中医养生和健康生活方式指导。
你的回答应该简洁、专业，并基于中医理论和现代医学知识。
当用户提供图片时，你应该分析图片内容并结合中医养生知识给出建议。
如果用户询问的问题超出你的知识范围，请诚实告知并建议咨询专业医生。
''';
  }

  /// 获取最近的消息记录
  List<Map<String, dynamic>> _getRecentMessages(int count) {
    if (_messages.length <= count) {
      return _messages;
    }
    return _messages.sublist(_messages.length - count);
  }

  /// 构建消息输入框
  Widget _buildMessageInput() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return ClipRRect(
      borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 8,
          ),
          decoration: BoxDecoration(
            color: isDarkMode
                ? Colors.grey.shade900.withAlpha(120)
                : Colors.white.withAlpha(120),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
            border: Border.all(
              color: isDarkMode
                  ? Colors.white.withAlpha(20)
                  : Colors.white.withAlpha(80),
              width: 0.5,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withAlpha(10),
                blurRadius: 4,
                offset: const Offset(0, -1),
              ),
            ],
          ),
          child: Row(
            children: [
              // 文本输入框
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: isDarkMode
                        ? Colors.grey.shade800.withAlpha(100)
                        : Colors.grey.shade100.withAlpha(100),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isDarkMode
                          ? Colors.white.withAlpha(20)
                          : Colors.grey.withAlpha(80),
                      width: 0.5,
                    ),
                  ),
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: '输入消息...',
                      hintStyle: TextStyle(
                        color: isDarkMode
                            ? Colors.grey.withAlpha(150)
                            : Colors.grey.withAlpha(180),
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                      border: InputBorder.none,
                    ),
                    maxLines: null,
                    keyboardType: TextInputType.multiline,
                    textCapitalization: TextCapitalization.sentences,
                    textInputAction: TextInputAction.send, // 将换行键改为发送键
                    onSubmitted: (text) {
                      if (text.trim().isNotEmpty) {
                        _handleMessageSend();
                      }
                    },
                    style: TextStyle(
                      color: isDarkMode
                          ? AppColors.darkTextPrimary
                          : AppColors.lightTextPrimary,
                    ),
                  ),
                ),
              ),

              const SizedBox(width: 8),

              // 加号按钮（更多选项）
              _buildInputButton(
                Icons.add_circle_outline,
                _showMoreOptions,
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建输入框按钮
  Widget _buildInputButton(
    IconData icon,
    VoidCallback onTap, {
    Color? color,
  }) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final buttonColor = color ??
        (isDarkMode ? AppColors.darkTextPrimary : AppColors.lightTextPrimary);

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: isDarkMode
              ? Colors.grey.shade800.withAlpha(100)
              : Colors.grey.shade100.withAlpha(100),
          shape: BoxShape.circle,
          border: Border.all(
            color: isDarkMode
                ? Colors.white.withAlpha(20)
                : Colors.grey.withAlpha(80),
            width: 0.5,
          ),
        ),
        child: Center(
          child: Icon(
            icon,
            size: 20,
            color: buttonColor,
          ),
        ),
      ),
    );
  }

  /// 处理热门话题点击
  void _handleHotTopicTap(String topic) {
    _messageController.text = topic;
  }

  /// 处理消息发送
  void _handleMessageSend() async {
    String message = _messageController.text.trim();
    if (message.isEmpty) return;

    // 添加用户消息
    setState(() {
      _messages.add({
        'sender': 'user',
        'content': message,
        'timestamp': DateTime.now(),
        'isRead': true,
      });

      // 显示处理中状态
      _isProcessing = true;
    });

    // 清空输入框
    _messageController.clear();

    // 无感采集文本数据
    _collectMultimodalData(message, 'text');

    // 无感采集环境数据
    _collectMultimodalData('', 'environment');

    // 清除选中的图片
    final hasImage = _selectedImagePath != null;
    final imagePath = _selectedImagePath;
    _selectedImagePath = null;

    try {
      // 收集用户消息数据
      final multimodalService = ref.read(multimodalDataServiceProvider);
      await multimodalService.collectTextData(_sessionId, message,
          label: 'user_message');

      // 使用DeepSeek API处理请求
      String aiResponse;

      if (hasImage) {
        // 如果有图片，使用多模态处理
        aiResponse = await multimodalService.processWithLLM(
          sessionId: _sessionId,
          prompt: message,
          imagePath: imagePath,
          systemMessage: _getSystemPrompt(),
        );
      } else {
        // 纯文本处理
        final deepseekService = ref.read(deepseekServiceProvider);
        final messages = [
          ChatMessage.system(_getSystemPrompt()),
          // 添加历史消息上下文（最多3条）
          ..._getRecentMessages(3).map((m) {
            return m['sender'] == 'user'
                ? ChatMessage.userText(m['content'])
                : ChatMessage.assistant(m['content']);
          }),
          // 添加当前消息
          ChatMessage.userText(message),
        ];

        aiResponse = await deepseekService.chat(messages: messages);

        // 收集AI回复
        await multimodalService.collectTextData(_sessionId, aiResponse,
            label: 'ai_response');
      }

      // 添加AI回复
      if (mounted) {
        setState(() {
          _messages.add({
            'sender': 'ai',
            'content': aiResponse,
            'timestamp': DateTime.now(),
            'isRead': true,
          });
          _isProcessing = false;
        });

        // 如果启用了语音回复，播放AI回复
        if (_autoVoiceReply) {
          _speakAIResponse(aiResponse);
        }
      }
    } catch (e) {
      debugPrint('处理消息失败: $e');

      // 添加错误回复
      if (mounted) {
        setState(() {
          _messages.add({
            'sender': 'ai',
            'content': '抱歉，我遇到了一些问题，无法正常回应。请稍后再试。',
            'timestamp': DateTime.now(),
            'isRead': true,
          });
          _isProcessing = false;
        });
      }
    }
  }

  /// 语音播报AI回复
  void _speakAIResponse(String text) async {
    try {
      // 这里可以接入TTS服务
      // 当前我们使用一个简单的提示来模拟
      if (_isCallActive) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(Icons.volume_up, color: Colors.white, size: 16),
                const SizedBox(width: 8),
                const Text('正在播放AI回复'),
              ],
            ),
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      debugPrint('语音回复失败: $e');
    }
  }

  /// 采集多模态数据
  void _collectMultimodalData(String data, String type) async {
    try {
      final multimodalService = ref.read(multimodalDataServiceProvider);

      switch (type) {
        case 'speech':
          await multimodalService.collectAudioData(_sessionId, data,
              label: 'user_speech');
          break;
        case 'text':
          await multimodalService.collectTextData(_sessionId, data,
              label: 'user_text');
          break;
        case 'environment':
          // 环境数据采集 - 将环境信息转换为文本格式
          final brightness =
              MediaQuery.of(context).platformBrightness.toString();
          final time = DateTime.now().hour;
          final environmentInfo =
              'env:brightness=$brightness;time=$time;device=mobile';

          // 使用文本数据方法存储环境信息
          await multimodalService.collectTextData(_sessionId, environmentInfo,
              label: 'environment_data');
          break;
      }
    } catch (e) {
      // 静默处理错误，不打断用户体验
      debugPrint('多模态数据采集失败: $e');
    }
  }

  /// 显示语音交互对话框
  void _showVoiceInteractionDialog() {
    // 显示语音功能提示
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.phone,
              color: AppColors.primaryColor,
              size: 24,
            ),
            const SizedBox(width: 8),
            const Text('语音对话'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              '您可以通过语音与AI助手直接对话，无需打字',
              style: TextStyle(fontSize: 14),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            CircleAvatar(
              radius: 36,
              backgroundColor: AppColors.primaryColor.withAlpha(30),
              child: Icon(
                Icons.mic,
                size: 40,
                color: AppColors.primaryColor,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              '点击开始语音对话',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Text(
              '提示：\n1. 请在安静的环境中使用\n2. 语音清晰，避免背景噪音\n3. 对话结束后点击"结束"按钮',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
            },
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _startVoiceInteraction();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primaryColor,
              foregroundColor: Colors.white,
            ),
            child: const Text('开始对话'),
          ),
        ],
      ),
    );
  }

  /// 开始语音交互（无需弹出对话框）
  void _startVoiceInteraction() async {
    try {
      // 请求麦克风权限
      final hasPermission = await PermissionUtils.requestMicrophonePermission();
      if (!hasPermission) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('需要麦克风权限才能使用语音对话功能'),
              duration: Duration(seconds: 2),
            ),
          );
        }
        return;
      }

      // 自动开启麦克风
      if (!_isMicrophoneOn) {
        _toggleMicrophone();
      }
    } catch (e) {
      debugPrint('语音交互启动失败: $e');
    }
  }

  void _toggleMicrophoneMute() async {
    // 如果通话不活跃，无法切换静音
    if (!_isCallActive) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('请先开始语音通话'),
          duration: Duration(seconds: 1),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    final speechService = ref.read(speechServiceProvider.notifier);

    if (_isMicrophoneOn) {
      // 静音
      await speechService.stopListening();
      setState(() {
        _isMicrophoneOn = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('麦克风已静音'),
          duration: Duration(seconds: 1),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } else {
      // 取消静音
      setState(() {
        _isMicrophoneOn = true;
      });

      _startVoiceRecognition();

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('麦克风已开启'),
          duration: Duration(seconds: 1),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  /// 开始语音识别
  void _startVoiceRecognition() async {
    try {
      final speechService = ref.read(speechServiceProvider.notifier);

      // 检查服务状态
      final currentState = ref.read(speechServiceProvider);
      debugPrint('当前语音服务状态: $currentState');

      // 如果服务处于错误状态，尝试强制重新初始化
      if (currentState == SpeechRecognitionStatus.error) {
        debugPrint('语音服务处于错误状态，尝试重新初始化');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('正在重新初始化语音服务...'),
            duration: Duration(seconds: 1),
          ),
        );

        final success = await speechService.forceReInitialize();
        if (!success) {
          debugPrint('语音服务重新初始化失败');
          if (mounted) {
            setState(() {
              _isMicrophoneOn = false;
            });

            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('语音服务初始化失败，请重启应用后再试'),
                duration: Duration(seconds: 3),
              ),
            );
          }
          return;
        }
      }

      // 开始语音识别，添加重试逻辑
      bool success = false;
      int retryCount = 0;
      const maxRetries = 2;

      while (!success && retryCount <= maxRetries) {
        success = await speechService.startListening(
          onResult: (text) {
            if (text.isNotEmpty) {
              // 自动采集多模态数据
              _collectMultimodalData(text, 'speech');

              // 更新输入框内容
              _messageController.text = text;
              // 同时更新状态，触发UI刷新
              ref.read(speechResultProvider.notifier).state = text;

              // 当识别到完整句子且长度超过5个字符时，自动发送消息
              if (text.trim().length > 5 &&
                  (text.endsWith('。') ||
                      text.endsWith('？') ||
                      text.endsWith('！'))) {
                _handleMessageSend();
              }
            }
          },
        );

        if (!success) {
          retryCount++;
          if (retryCount <= maxRetries) {
            debugPrint('语音识别启动失败，尝试重试 ($retryCount/$maxRetries)');
            // 短暂延迟后重试
            await Future.delayed(const Duration(milliseconds: 500));
          }
        }
      }

      if (!success && mounted) {
        setState(() {
          _isMicrophoneOn = false;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('语音识别服务启动失败，请确保已授予麦克风权限并重试'),
            duration: Duration(seconds: 3),
          ),
        );
      } else if (success) {
        // 启动成功
        debugPrint('语音识别启动成功');
      }
    } catch (e) {
      debugPrint('语音识别启动失败: $e');
      if (mounted) {
        setState(() {
          _isMicrophoneOn = false;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('语音识别出错: $e'),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    }
  }

  /// 构建浮动语音指示器
  Widget _buildFloatingVoiceIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.primaryColor.withAlpha(30),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.primaryColor.withAlpha(60),
          width: 0.5,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 脉冲动画的麦克风图标
          TweenAnimationBuilder<double>(
            tween: Tween<double>(begin: 0.8, end: 1.0),
            duration: const Duration(milliseconds: 800),
            curve: Curves.easeInOut,
            builder: (context, value, child) {
              return Icon(
                _isMicrophoneOn ? Icons.mic : Icons.mic_off,
                color: _isMicrophoneOn ? AppColors.primaryColor : Colors.grey,
                size: 16 * value,
              );
            },
            onEnd: () {
              setState(() {}); // 重新触发动画
            },
          ),
          const SizedBox(width: 8),
          Text(
            _isMicrophoneOn ? '语音已开启' : '语音已暂停',
            style: TextStyle(
              fontSize: 12,
              color: _isMicrophoneOn ? AppColors.primaryColor : Colors.grey,
            ),
          ),
        ],
      ),
    );
  }

  /// 显示AI代理设置
  void _showAIAgentSettings() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) {
        final isDarkMode = Theme.of(context).brightness == Brightness.dark;

        return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isDarkMode ? Colors.grey.shade900 : Colors.white,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'AI设置',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              ListTile(
                leading: Icon(
                  Icons.psychology,
                  color: AppColors.primaryColor,
                ),
                title: const Text('AI模型'),
                subtitle: const Text('当前：索克生活基础模型'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  Navigator.pop(context);
                  _showModelSelectionDialog();
                },
              ),
              ListTile(
                leading: Icon(
                  Icons.memory,
                  color: AppColors.primaryColor,
                ),
                title: const Text('知识库设置'),
                subtitle: const Text('个性化知识增强'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  Navigator.pop(context);
                  _showKnowledgeBaseSettings();
                },
              ),
              ListTile(
                leading: Icon(
                  Icons.settings_voice,
                  color: AppColors.primaryColor,
                ),
                title: const Text('语音设置'),
                subtitle: const Text('调整语音识别与合成'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  Navigator.pop(context);
                  _showVoiceSettings();
                },
              ),
            ],
          ),
        );
      },
    );
  }

  /// 显示AI模型选择对话框
  void _showModelSelectionDialog() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('选择AI模型'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: const Text('索克生活基础模型'),
              subtitle: const Text('通用型AI助手，均衡的性能和效率'),
              value: 'base',
              groupValue: 'base', // 当前选中的值
              onChanged: (value) {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('已选择基础模型')),
                );
              },
              activeColor: AppColors.primaryColor,
            ),
            RadioListTile<String>(
              title: const Text('中医专业增强模型'),
              subtitle: const Text('专注中医领域，提供专业诊疗建议'),
              value: 'tcm',
              groupValue: 'base', // 当前选中的值
              onChanged: (value) {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('中医专业模型即将推出，敬请期待')),
                );
              },
              activeColor: AppColors.primaryColor,
            ),
            RadioListTile<String>(
              title: const Text('营养学专家模型'),
              subtitle: const Text('专注饮食营养领域，提供精准膳食建议'),
              value: 'nutrition',
              groupValue: 'base', // 当前选中的值
              onChanged: (value) {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('营养学专家模型即将推出，敬请期待')),
                );
              },
              activeColor: AppColors.primaryColor,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  /// 显示知识库设置
  void _showKnowledgeBaseSettings() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('知识库设置'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SwitchListTile(
              title: const Text('中医经典知识库'),
              subtitle: const Text('包含黄帝内经、伤寒论等经典著作'),
              value: true,
              onChanged: (value) {},
              activeColor: AppColors.primaryColor,
            ),
            SwitchListTile(
              title: const Text('现代医学知识库'),
              subtitle: const Text('包含现代医学研究成果和临床指南'),
              value: true,
              onChanged: (value) {},
              activeColor: AppColors.primaryColor,
            ),
            SwitchListTile(
              title: const Text('我的健康数据'),
              subtitle: const Text('基于您的健康数据进行个性化推荐'),
              value: true,
              onChanged: (value) {},
              activeColor: AppColors.primaryColor,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primaryColor,
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 40),
              ),
              child: const Text('添加自定义知识库'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('知识库设置已保存')),
              );
            },
            child: const Text('保存'),
          ),
        ],
      ),
    );
  }

  /// 显示语音设置
  void _showVoiceSettings() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(builder: (context, setState) {
        return AlertDialog(
          title: const Text('语音设置'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                title: const Text('语音识别灵敏度'),
                subtitle: Slider(
                  value: 0.7,
                  onChanged: (value) {},
                  activeColor: AppColors.primaryColor,
                ),
              ),
              ListTile(
                title: const Text('语音合成速度'),
                subtitle: Slider(
                  value: 0.5,
                  onChanged: (value) {},
                  activeColor: AppColors.primaryColor,
                ),
              ),
              SwitchListTile(
                title: const Text('自动语音回复'),
                subtitle: const Text('收到消息后自动语音播报'),
                value: _autoVoiceReply,
                onChanged: (value) {
                  setState(() {
                    _autoVoiceReply = value;
                  });
                  // 更新外层状态
                  this.setState(() {});
                },
                activeColor: AppColors.primaryColor,
              ),
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: '语音合成声音',
                ),
                value: '女声1',
                items: const [
                  DropdownMenuItem(value: '女声1', child: Text('女声1 - 标准普通话')),
                  DropdownMenuItem(value: '男声1', child: Text('男声1 - 标准普通话')),
                  DropdownMenuItem(value: '女声2', child: Text('女声2 - 温柔亲切')),
                  DropdownMenuItem(value: '男声2', child: Text('男声2 - 沉稳专业')),
                ],
                onChanged: (value) {},
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('语音设置已保存')),
                );
              },
              child: const Text('保存'),
            ),
          ],
        );
      }),
    );
  }

  /// 显示更多选项
  void _showMoreOptions() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isDarkMode ? Colors.grey.shade900 : Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              '更多选项',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),

            // 媒体选项
            Row(
              children: [
                Expanded(
                  child: Text(
                    '媒体',
                    style: TextStyle(
                      fontSize: 14,
                      color: isDarkMode
                          ? Colors.grey.shade400
                          : Colors.grey.shade700,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(),

            // 媒体选项
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildOptionItem(
                  icon: Icons.image,
                  label: '发送图片',
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(false);
                  },
                ),
                _buildOptionItem(
                  icon: Icons.camera_alt,
                  label: '拍摄照片',
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(true);
                  },
                ),
                _buildOptionItem(
                  icon: Icons.file_present,
                  label: '发送文件',
                  onTap: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('文件上传功能即将推出')),
                    );
                  },
                ),
                _buildOptionItem(
                  icon: Icons.location_on,
                  label: '发送位置',
                  onTap: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('位置分享功能即将推出')),
                    );
                  },
                ),
              ],
            ),

            const SizedBox(height: 16),

            // 中医测评选项
            Row(
              children: [
                Expanded(
                  child: Text(
                    '中医测评',
                    style: TextStyle(
                      fontSize: 14,
                      color: isDarkMode
                          ? Colors.grey.shade400
                          : Colors.grey.shade700,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(),

            // 中医测评选项
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildOptionItem(
                  icon: Icons.favorite,
                  label: '脉诊分析',
                  onTap: () {
                    Navigator.pop(context);
                    _startPulseDiagnosis();
                  },
                ),
                _buildOptionItem(
                  icon: Icons.catching_pokemon,
                  label: '舌诊分析',
                  onTap: () {
                    Navigator.pop(context);
                    _startTongueDiagnosis();
                  },
                ),
                _buildOptionItem(
                  icon: Icons.face,
                  label: '面诊分析',
                  onTap: () {
                    Navigator.pop(context);
                    _startFaceDiagnosis();
                  },
                ),
                _buildOptionItem(
                  icon: Icons.assessment,
                  label: '体质测评',
                  onTap: () {
                    Navigator.pop(context);
                    _startConstitutionAssessment();
                  },
                ),
              ],
            ),

            const SizedBox(height: 16),

            // 心理测评选项
            Row(
              children: [
                Expanded(
                  child: Text(
                    '心理测评',
                    style: TextStyle(
                      fontSize: 14,
                      color: isDarkMode
                          ? Colors.grey.shade400
                          : Colors.grey.shade700,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(),

            // 心理测评选项
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildOptionItem(
                  icon: Icons.psychology,
                  label: 'MBTI测试',
                  onTap: () {
                    Navigator.pop(context);
                    _startMBTITest();
                  },
                ),
                _buildOptionItem(
                  icon: Icons.hub,
                  label: '九型人格',
                  onTap: () {
                    Navigator.pop(context);
                    _startEnneagramTest();
                  },
                ),
                _buildOptionItem(
                  icon: Icons.mood,
                  label: '情绪分析',
                  onTap: () {
                    Navigator.pop(context);
                    _startEmotionAnalysis();
                  },
                ),
                _buildOptionItem(
                  icon: Icons.self_improvement,
                  label: '压力评估',
                  onTap: () {
                    Navigator.pop(context);
                    _startStressAssessment();
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// 构建选项项
  Widget _buildOptionItem({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: (MediaQuery.of(context).size.width - 56) / 4,
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              decoration: BoxDecoration(
                color: AppColors.primaryColor.withAlpha(isDarkMode ? 40 : 30),
                shape: BoxShape.circle,
              ),
              padding: const EdgeInsets.all(10),
              child: Icon(
                icon,
                color: AppColors.primaryColor,
                size: 24,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: isDarkMode ? Colors.grey.shade300 : Colors.grey.shade800,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  /// 启动脉诊分析
  void _startPulseDiagnosis() async {
    try {
      // 向聊天添加提示消息
      setState(() {
        _messages.add({
          'sender': 'ai',
          'content': '请将手机靠近手腕脉搏处，保持稳定，我将通过摄像头和传感器采集您的脉搏信息进行分析。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });

      // 导航到脉诊分析页面
      final result = await context.router.push(PulseDiagnosisRoute());

      if (result != null && result is Map<String, dynamic>) {
        // 将结果添加到聊天中
        setState(() {
          _messages.add({
            'sender': 'user',
            'content': '我完成了脉诊分析',
            'timestamp': DateTime.now(),
            'isRead': true,
          });

          _messages.add({
            'sender': 'ai',
            'content':
                '根据脉诊分析，您的脉象呈现${result['pulseType']}特征，${result['analysis']}。\n\n这可能与${result['relation']}有关，建议您${result['suggestion']}。',
            'timestamp': DateTime.now(),
            'isRead': true,
          });
        });
      }
    } catch (e) {
      debugPrint('启动脉诊分析失败: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('无法启动脉诊分析: $e')),
      );
    }
  }

  /// 启动舌诊分析
  void _startTongueDiagnosis() async {
    try {
      // 向聊天添加提示消息
      setState(() {
        _messages.add({
          'sender': 'ai',
          'content': '请在光线充足的环境下，对准舌头，保持口腔清洁，我将通过摄像头采集您的舌象信息进行分析。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });

      // 导航到舌诊分析页面
      final result = await context.router.push(TongueDiagnosisRoute());

      if (result != null && result is TongueDiagnosisResult) {
        // 将结果添加到聊天中
        setState(() {
          _messages.add({
            'sender': 'user',
            'content': '我完成了舌诊分析',
            'timestamp': DateTime.now(),
            'isRead': true,
          });

          _messages.add({
            'sender': 'ai',
            'content':
                '${result.analysisText}\n\n这可能与${result.constitutions.join('、')}体质有关，建议您${result.suggestions.join('，')}。',
            'timestamp': DateTime.now(),
            'isRead': true,
          });
        });
      }
    } catch (e) {
      debugPrint('启动舌诊分析失败: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('无法启动舌诊分析: $e')),
      );
    }
  }

  /// 启动面诊分析
  void _startFaceDiagnosis() async {
    try {
      // 向聊天添加提示消息
      setState(() {
        _messages.add({
          'sender': 'ai',
          'content': '面诊是中医四诊之一，通过观察面部特征来评估健康状况。请在光线充足的环境下，面对摄像头，保持自然表情。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });

      // 目前功能尚未实现，返回提示信息
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _messages.add({
          'sender': 'user',
          'content': '我想进行面诊分析',
          'timestamp': DateTime.now(),
          'isRead': true,
        });

        _messages.add({
          'sender': 'ai',
          'content':
              '面诊分析功能正在开发中，将很快推出。面诊是中医传统诊断方法，通过观察面部色泽、五官特征等，判断内脏功能状态。\n\n传统中医认为，面部不同区域对应不同的脏腑:\n· 额头 - 对应心脏\n· 鼻子 - 对应脾胃\n· 双颊 - 对应肺部\n· 下巴 - 对应肾脏\n\n请持续关注，面诊功能即将上线。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });
    } catch (e) {
      debugPrint('启动面诊分析失败: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('无法启动面诊分析: $e')),
      );
    }
  }

  /// 启动体质测评
  void _startConstitutionAssessment() async {
    try {
      // 向聊天添加提示消息
      setState(() {
        _messages.add({
          'sender': 'ai',
          'content': '中医体质测评是评估您体质类型的重要方法，需要回答一系列关于您的生理、心理特点和生活习惯的问题。准备好了吗？',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });

      // 目前功能尚未实现，返回提示信息
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _messages.add({
          'sender': 'user',
          'content': '我想进行体质测评',
          'timestamp': DateTime.now(),
          'isRead': true,
        });

        _messages.add({
          'sender': 'ai',
          'content':
              '体质测评功能正在开发中，将很快推出。中医体质理论将人的体质分为九种基本类型：平和质、气虚质、阳虚质、阴虚质、痰湿质、湿热质、气郁质、血瘀质和特禀质。\n\n不同体质的人在生理、心理特点以及对环境的适应能力等方面都有所不同，也更易患某些疾病。体质测评将帮助您了解自己的体质类型，从而提供针对性的养生建议。\n\n请持续关注，体质测评功能即将上线。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });
    } catch (e) {
      debugPrint('启动体质测评失败: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('无法启动体质测评: $e')),
      );
    }
  }

  /// 启动MBTI测试
  void _startMBTITest() async {
    try {
      // 向聊天添加提示消息
      setState(() {
        _messages.add({
          'sender': 'ai',
          'content':
              'MBTI(迈尔斯-布里格斯类型指标)是一种流行的人格类型测试，可以帮助您了解自己的性格特点和沟通方式。准备好开始测试了吗？',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });

      // 目前功能尚未实现，返回提示信息
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _messages.add({
          'sender': 'user',
          'content': '我想进行MBTI测试',
          'timestamp': DateTime.now(),
          'isRead': true,
        });

        _messages.add({
          'sender': 'ai',
          'content':
              'MBTI测试功能正在开发中，将很快推出。MBTI将人格分为16种类型，基于四个维度的偏好：\n\n· 精力方向：外向(E)或内向(I)\n· 信息获取：感觉(S)或直觉(N)\n· 决策方式：思考(T)或情感(F)\n· 生活方式：判断(J)或认知(P)\n\n了解您的MBTI类型有助于更好地认识自己的优势和挑战，改善人际关系，指导职业发展。\n\n请持续关注，MBTI测试功能即将上线。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });
    } catch (e) {
      debugPrint('启动MBTI测试失败: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('无法启动MBTI测试: $e')),
      );
    }
  }

  /// 启动九型人格测试
  void _startEnneagramTest() async {
    try {
      // 向聊天添加提示消息
      setState(() {
        _messages.add({
          'sender': 'ai',
          'content': '九型人格(Enneagram)是一种深入的人格理论，描述了九种不同的人格类型及其相互关系。准备好开始测试了吗？',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });

      // 目前功能尚未实现，返回提示信息
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _messages.add({
          'sender': 'user',
          'content': '我想进行九型人格测试',
          'timestamp': DateTime.now(),
          'isRead': true,
        });

        _messages.add({
          'sender': 'ai',
          'content':
              '九型人格测试功能正在开发中，将很快推出。九型人格将人分为九种基本类型：\n\n· 一号：完美主义者\n· 二号：助人者\n· 三号：成就者\n· 四号：个人主义者\n· 五号：思想家\n· 六号：忠诚者\n· 七号：探险家\n· 八号：领导者\n· 九号：调解者\n\n了解您的九型人格类型有助于认识自己的核心动机、恐惧和防御机制，促进个人成长和自我发展。\n\n请持续关注，九型人格测试功能即将上线。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });
    } catch (e) {
      debugPrint('启动九型人格测试失败: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('无法启动九型人格测试: $e')),
      );
    }
  }

  /// 启动情绪分析
  void _startEmotionAnalysis() async {
    try {
      // 向聊天添加提示消息
      setState(() {
        _messages.add({
          'sender': 'ai',
          'content': '情绪分析可以帮助您识别和理解自己的情绪状态，从而更好地进行情绪管理。准备好开始分析了吗？',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });

      // 目前功能尚未实现，返回提示信息
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _messages.add({
          'sender': 'user',
          'content': '我想进行情绪分析',
          'timestamp': DateTime.now(),
          'isRead': true,
        });

        _messages.add({
          'sender': 'ai',
          'content':
              '情绪分析功能正在开发中，将很快推出。情绪分析通过分析表情、语音、文字等多种方式，评估您的情绪状态，包括喜悦、悲伤、愤怒、恐惧、厌恶、惊讶等基本情绪，以及更复杂的情绪组合。\n\n中医认为情绪与五脏关系密切：\n· 怒伤肝\n· 喜伤心\n· 思伤脾\n· 忧伤肺\n· 恐伤肾\n\n了解并管理情绪对身心健康至关重要。\n\n请持续关注，情绪分析功能即将上线。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });
    } catch (e) {
      debugPrint('启动情绪分析失败: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('无法启动情绪分析: $e')),
      );
    }
  }

  /// 启动压力评估
  void _startStressAssessment() async {
    try {
      // 向聊天添加提示消息
      setState(() {
        _messages.add({
          'sender': 'ai',
          'content': '压力评估可以帮助您了解自己当前的压力水平和压力来源，从而采取适当的减压方法。准备好开始评估了吗？',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });

      // 目前功能尚未实现，返回提示信息
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _messages.add({
          'sender': 'user',
          'content': '我想进行压力评估',
          'timestamp': DateTime.now(),
          'isRead': true,
        });

        _messages.add({
          'sender': 'ai',
          'content':
              '压力评估功能正在开发中，将很快推出。压力评估通过问卷、心率变异性(HRV)分析、皮肤电反应等方式，综合评估您的压力水平。\n\n长期的高压力状态可能导致：\n· 睡眠质量下降\n· 免疫功能减弱\n· 消化问题\n· 心血管健康风险增加\n· 情绪波动\n\n中医认为过度的压力会导致气机郁滞，影响气血运行。了解自己的压力状态，采取适当的减压方法，对维护健康至关重要。\n\n请持续关注，压力评估功能即将上线。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });
    } catch (e) {
      debugPrint('启动压力评估失败: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('无法启动压力评估: $e')),
      );
    }
  }

  /// 选择图片
  Future<void> _pickImage(bool fromCamera) async {
    try {
      final multimodalService = ref.read(multimodalDataServiceProvider);
      final appConfig = ref.read(appConfigProvider);

      // 收集图像数据
      final imagePath = await multimodalService.collectImageData(
        _sessionId,
        fromCamera: fromCamera,
        label: 'user_image',
      );

      if (imagePath != null) {
        // 获取图片类型
        final imageItem = _getLastImageItem(_sessionId);
        final contentType = imageItem?['contentType'] as String?;

        setState(() {
          _selectedImagePath = imagePath;
        });

        // 如果是舌头图片且配置了自动识别，直接进入舌诊流程
        if (contentType == 'tongue' && appConfig.autoDetectTongueImages) {
          _handleTongueImageDetected(imagePath);
          return;
        }

        // 提示用户图片已选择
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.green, size: 16),
                const SizedBox(width: 8),
                Text(contentType == 'tongue'
                    ? '检测到舌头图片，您可以开始输入描述，或直接进行舌诊分析'
                    : '图片已选择，请输入描述并发送'),
              ],
            ),
            action: contentType == 'tongue'
                ? SnackBarAction(
                    label: '舌诊分析',
                    onPressed: () {
                      _handleTongueImageDetected(imagePath);
                    },
                  )
                : SnackBarAction(
                    label: '取消',
                    onPressed: () {
                      setState(() {
                        _selectedImagePath = null;
                      });
                    },
                  ),
          ),
        );
      }
    } catch (e) {
      debugPrint('选择图片失败: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('选择图片失败: $e')),
      );
    }
  }

  /// 处理已检测到的舌头图片
  Future<void> _handleTongueImageDetected(String imagePath) async {
    // 清除选中的图片（因为会进入舌诊流程）
    setState(() {
      _selectedImagePath = null;
    });

    // 添加舌诊提示消息
    setState(() {
      _messages.add({
        'sender': 'ai',
        'content': '我检测到您上传了舌头图片，正在为您进行舌诊分析...',
        'timestamp': DateTime.now(),
        'isRead': true,
      });
    });

    // 调用舌诊服务
    try {
      final result =
          await context.router.push(TongueDiagnosisRoute(imagePath: imagePath));

      if (result != null && result is TongueDiagnosisResult) {
        // 将结果添加到聊天中
        setState(() {
          _messages.add({
            'sender': 'user',
            'content': '我上传了舌头图片进行分析',
            'timestamp': DateTime.now(),
            'isRead': true,
          });

          _messages.add({
            'sender': 'ai',
            'content':
                '${result.analysisText}\n\n这可能与${result.constitutions.join('、')}体质有关，建议您${result.suggestions.join('，')}。',
            'timestamp': DateTime.now(),
            'isRead': true,
          });
        });
      }
    } catch (e) {
      debugPrint('舌诊分析失败: $e');
      // 显示错误消息
      setState(() {
        _messages.add({
          'sender': 'ai',
          'content': '很抱歉，舌诊分析过程中遇到了问题，请稍后再试。',
          'timestamp': DateTime.now(),
          'isRead': true,
        });
      });
    }
  }

  /// 获取最后一个图片项
  Map<String, dynamic>? _getLastImageItem(String sessionId) {
    final multimodalService = ref.read(multimodalDataServiceProvider);
    return multimodalService.getLastItemOfType(_sessionId, 'image');
  }

  /// 处理语音输入
  void _handleVoiceInput() async {
    try {
      final hasPermission = await PermissionUtils.requestMicrophonePermission();
      if (!hasPermission) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('需要麦克风权限才能使用语音输入功能'),
              duration: Duration(seconds: 2),
            ),
          );
        }
        return;
      }

      // 切换麦克风状态以开始语音输入
      _toggleMicrophone();

      // 显示语音输入提示
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('请开始说话，系统会自动将您的语音转换为文字'),
          duration: Duration(seconds: 2),
        ),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('无法启动语音输入: $e'),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    }
  }

  /// 添加欢迎消息
  void _addWelcomeMessage() {
    final now = DateTime.now();
    String greeting = '你好！';

    // 根据时间段选择不同的问候语
    if (now.hour >= 5 && now.hour < 12) {
      greeting = '早上好！';
    } else if (now.hour >= 12 && now.hour < 18) {
      greeting = '下午好！';
    } else if (now.hour >= 18 && now.hour < 22) {
      greeting = '晚上好！';
    } else {
      greeting = '夜深了，';
    }

    setState(() {
      _messages.add({
        'sender': 'ai',
        'content': '$greeting我是索克AI助手，很高兴为您服务。您可以直接对我说话，询问健康养生、中医调理或日常生活方面的问题。',
        'timestamp': DateTime.now(),
        'isRead': true,
      });

      // 添加提示用户开启麦克风权限的消息
      if (!_isMicrophoneOn) {
        _messages.add({
          'sender': 'ai',
          'content': '要体验语音交互功能，请点击右上角的麦克风图标并授予权限。您随时可以通过语音与我交流，让沟通更加便捷。',
          'timestamp': DateTime.now().add(const Duration(seconds: 1)),
          'isRead': true,
        });
      }
    });
  }

  /// 构建语音指示器
  Widget _buildVoiceIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 16),
      color: AppColors.primaryColor.withAlpha(30),
      child: Row(
        children: [
          Icon(
            Icons.mic,
            color: AppColors.primaryColor,
            size: 16,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '语音识别已开启，直接说话即可',
              style: TextStyle(
                fontSize: 12,
                color: AppColors.primaryColor,
              ),
            ),
          ),
          GestureDetector(
            onTap: () {
              if (_isMicrophoneOn) {
                _toggleMicrophone();
              }
            },
            child: Padding(
              padding: const EdgeInsets.all(4.0),
              child: Text(
                '关闭',
                style: TextStyle(
                  fontSize: 12,
                  color: AppColors.primaryColor,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建通话按钮（带动画效果）
  Widget _buildCallButton() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    // 通话活跃时为红色，否则为绿色
    final buttonColor = _isCallActive ? Colors.red : AppColors.successColor;

    // 通话活跃状态下有脉动动画效果
    return _isCallActive
        ? _buildPulsingCallButton(buttonColor, isDarkMode)
        : _buildStaticCallButton(buttonColor, isDarkMode);
  }

  /// 构建脉动效果的通话按钮
  Widget _buildPulsingCallButton(Color buttonColor, bool isDarkMode) {
    return GestureDetector(
      onTap: _endCall,
      child: TweenAnimationBuilder<double>(
        tween: Tween<double>(begin: 0.8, end: 1.0),
        duration: const Duration(milliseconds: 800),
        curve: Curves.easeInOut,
        builder: (context, value, child) {
          return AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: buttonColor.withAlpha((40 * value).toInt()),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: buttonColor.withAlpha((60 * value).toInt()),
                width: 1.5,
              ),
            ),
            child: Icon(
              Icons.phone,
              size: 22 * value,
              color: buttonColor,
            ),
          );
        },
        onEnd: () {
          // 动画结束后重新开始，实现脉动效果
          setState(() {});
        },
      ),
    );
  }

  /// 构建静态的通话按钮
  Widget _buildStaticCallButton(Color buttonColor, bool isDarkMode) {
    return GestureDetector(
      onTap: _startCall,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: buttonColor.withAlpha(30),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: buttonColor.withAlpha(50),
                width: 0.5,
              ),
            ),
            child: Icon(
              Icons.phone,
              size: 22,
              color: buttonColor,
            ),
          ),
        ),
      ),
    );
  }

  /// 开始语音通话
  void _startCall() async {
    if (_isCallActive) return;

    // 请求麦克风权限
    final hasPermission = await PermissionUtils.requestMicrophonePermission();
    if (!hasPermission) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('需要麦克风权限才能使用语音对话功能'),
            duration: Duration(seconds: 2),
          ),
        );
      }
      return;
    }

    // 更新通话状态
    setState(() {
      _isCallActive = true;
      _isMicrophoneOn = true;
    });

    // 开启麦克风
    _startVoiceRecognition();

    // 提示用户通话已开始
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('语音通话已开始，您可以直接说话'),
        duration: Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// 结束语音通话
  void _endCall() {
    if (!_isCallActive) return;

    // 停止语音识别
    final speechService = ref.read(speechServiceProvider.notifier);
    speechService.stopListening();

    // 更新通话状态
    setState(() {
      _isCallActive = false;
      _isMicrophoneOn = false;
    });

    // 提示用户通话已结束
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('语音通话已结束'),
        duration: Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// 构建麦克风按钮
  Widget _buildMicButton() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    // 计算按钮颜色 - 麦克风激活状态使用主色调
    final buttonColor = _isMicrophoneOn
        ? AppColors.primaryColor
        : (isDarkMode ? AppColors.darkTextPrimary : AppColors.lightTextPrimary);

    // 计算背景色 - 麦克风激活状态使用半透明主色调背景
    final backgroundColor = _isMicrophoneOn
        ? AppColors.primaryColor.withAlpha(30)
        : (isDarkMode ? Colors.white : Colors.black).withAlpha(15);

    return GestureDetector(
      onTap: _toggleMicrophone,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: backgroundColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: (isDarkMode ? Colors.white : Colors.black).withAlpha(30),
                width: 0.5,
              ),
            ),
            child: Icon(
              _isMicrophoneOn ? Icons.mic : Icons.mic_off,
              size: 22,
              color: buttonColor,
            ),
          ),
        ),
      ),
    );
  }
}
