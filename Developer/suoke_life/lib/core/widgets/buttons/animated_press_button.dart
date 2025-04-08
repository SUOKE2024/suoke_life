import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:flutter/services.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/theme/app_spacing.dart';
import 'package:suoke_life/core/theme/app_shapes.dart';

/// 3D按压按钮
///
/// 带有真实3D按压效果的按钮，提供更好的触感反馈
/// 基于弹簧物理模型实现平滑的按压动画
class AnimatedPressButton extends StatefulWidget {
  /// 按钮标签文本
  final String label;

  /// 点击回调
  final VoidCallback onPressed;

  /// 按钮图标
  final IconData? icon;

  /// 图标位置
  final IconPosition iconPosition;

  /// 按钮背景色
  final Color backgroundColor;

  /// 按钮文本颜色
  final Color textColor;

  /// 阴影颜色
  final Color shadowColor;

  /// 按钮高度
  final double height;

  /// 按钮宽度 (null为自适应)
  final double? width;

  /// 按钮圆角半径
  final double borderRadius;

  /// 3D效果深度 (下沉程度)
  final double depth;

  /// 是否启用触感反馈
  final bool enableHapticFeedback;

  /// 是否禁用
  final bool isDisabled;

  const AnimatedPressButton({
    Key? key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.iconPosition = IconPosition.left,
    this.backgroundColor = AppColors.primaryColor,
    this.textColor = Colors.white,
    this.shadowColor = Colors.black,
    this.height = 50.0,
    this.width,
    this.borderRadius = 12.0,
    this.depth = 4.0,
    this.enableHapticFeedback = true,
    this.isDisabled = false,
  }) : super(key: key);

  @override
  State<AnimatedPressButton> createState() => _AnimatedPressButtonState();
}

class _AnimatedPressButtonState extends State<AnimatedPressButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _pressAnimation;

  // 按钮的当前位移值 (0.0 -> 1.0)
  double _currentValue = 0.0;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();

    // 创建动画控制器
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 150),
    );

    // 设置弹簧物理模型
    final SpringSimulation spring = SpringSimulation(
      const SpringDescription(
        mass: 1.0,
        stiffness: 500.0,
        damping: 20.0,
      ),
      0.0, // 开始值
      1.0, // 结束值
      0.0, // 初始速度
    );

    // 创建按压动画
    _pressAnimation = _controller.drive(
      Tween<double>(begin: 0.0, end: 1.0),
    );

    // 监听动画值变化
    _pressAnimation.addListener(() {
      setState(() {
        _currentValue = _pressAnimation.value;
      });
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  // 处理按下事件
  void _handleTapDown(TapDownDetails details) {
    if (widget.isDisabled) return;

    _isPressed = true;
    _controller.animateTo(1.0);

    if (widget.enableHapticFeedback) {
      HapticFeedback.lightImpact();
    }
  }

  // 处理抬起事件
  void _handleTapUp(TapUpDetails details) {
    if (widget.isDisabled) return;

    _isPressed = false;
    _controller.animateBack(0.0);

    widget.onPressed();

    if (widget.enableHapticFeedback) {
      HapticFeedback.mediumImpact();
    }
  }

  // 处理取消事件
  void _handleTapCancel() {
    if (_isPressed) {
      _isPressed = false;
      _controller.animateBack(0.0);
    }
  }

  @override
  Widget build(BuildContext context) {
    // 计算按钮的垂直偏移
    final double yOffset = _currentValue * widget.depth;

    // 计算阴影的不透明度和模糊半径
    final double shadowOpacity = (1.0 - _currentValue) * 0.5;
    final double blurRadius = (1.0 - _currentValue) * 8.0 + 4.0;

    // 设置文字和背景色
    final Color effectiveBackgroundColor =
        widget.isDisabled ? Colors.grey.shade300 : widget.backgroundColor;

    final Color effectiveTextColor =
        widget.isDisabled ? Colors.grey.shade600 : widget.textColor;

    // 构建按钮内容
    Widget buttonContent = Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (widget.icon != null &&
            widget.iconPosition == IconPosition.left) ...[
          Icon(widget.icon, color: effectiveTextColor, size: 20),
          SizedBox(width: AppSpacing.xs),
        ],
        Text(
          widget.label,
          style: TextStyle(
            color: effectiveTextColor,
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        if (widget.icon != null &&
            widget.iconPosition == IconPosition.right) ...[
          SizedBox(width: AppSpacing.xs),
          Icon(widget.icon, color: effectiveTextColor, size: 20),
        ],
      ],
    );

    return SizedBox(
      width: widget.width,
      height: widget.height,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // 底部阴影 (3D效果的底座)
          Positioned(
            left: 0,
            right: 0,
            top: widget.depth,
            child: Container(
              height: widget.height - widget.depth,
              decoration: BoxDecoration(
                color: widget.shadowColor.withAlpha((0.2 * 255).toInt()),
                borderRadius: BorderRadius.circular(widget.borderRadius),
              ),
            ),
          ),

          // 主按钮
          AnimatedPositioned(
            duration: Duration.zero,
            left: 0,
            right: 0,
            top: yOffset,
            child: GestureDetector(
              onTapDown: _handleTapDown,
              onTapUp: _handleTapUp,
              onTapCancel: _handleTapCancel,
              child: Container(
                height: widget.height - widget.depth,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: effectiveBackgroundColor,
                  borderRadius: BorderRadius.circular(widget.borderRadius),
                  boxShadow: [
                    BoxShadow(
                      color: widget.shadowColor.withAlpha((shadowOpacity * 255).toInt()),
                      blurRadius: blurRadius,
                      offset: Offset(0, 2 * (1 - _currentValue)),
                    ),
                  ],
                ),
                child: buttonContent,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// 图标位置枚举
enum IconPosition {
  /// 图标在文字左侧
  left,

  /// 图标在文字右侧
  right,
}
