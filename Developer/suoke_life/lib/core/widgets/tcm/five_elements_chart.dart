import 'package:flutter/material.dart';
import 'dart:math' as math;
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/theme/tcm_visuals/five_elements.dart';
import 'package:suoke_life/core/widgets/tcm/five_element_shape.dart';
import 'package:suoke_life/core/widgets/tcm/models/five_elements_data.dart';

/// 五行关系图类型
enum FiveElementsChartType {
  /// 环形布局
  circular,

  /// 星形布局
  star,

  /// 直线布局
  linear,
}

/// 五行元素组件 - 用于构建五行图表中的单个元素
class _ElementNode extends StatelessWidget {
  /// 元素类型
  final ElementType elementType;

  /// 元素尺寸
  final double size;

  /// 元素值（0.0-1.0）
  final double value;

  /// 元素位置
  final Offset position;

  /// 点击回调
  final VoidCallback? onTap;

  /// 是否启用呼吸动画
  final bool enableBreathing;

  /// 构造函数
  const _ElementNode({
    Key? key,
    required this.elementType,
    required this.size,
    required this.value,
    required this.position,
    this.onTap,
    this.enableBreathing = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // 元素大小根据值缩放（最小为原始尺寸的70%）
    final scaledSize = size * (0.7 + value * 0.3);

    return Positioned(
      left: position.dx - scaledSize / 2,
      top: position.dy - scaledSize / 2,
      child: GestureDetector(
        onTap: onTap,
        child: FiveElementShape(
          elementType: elementType,
          size: scaledSize,
          enableBreathing: enableBreathing,
          hasShadow: true,
        ),
      ),
    );
  }
}

/// 五行关系线 - 用于绘制元素间的关系线
class _RelationLine extends StatelessWidget {
  /// 起点
  final Offset start;

  /// 终点
  final Offset end;

  /// 关系类型
  final ElementRelationType relationType;

  /// 线条宽度
  final double lineWidth;

  /// 关系强度
  final double strength;

  /// 是否带有箭头
  final bool hasArrow;

  /// 构造函数
  const _RelationLine({
    Key? key,
    required this.start,
    required this.end,
    required this.relationType,
    this.lineWidth = 2.0,
    this.strength = 1.0,
    this.hasArrow = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    Color lineColor;
    StrokeCap cap;

    // 根据关系类型设置线条样式
    switch (relationType) {
      case ElementRelationType.generating:
      case ElementRelationType.generated:
        lineColor = AppColors.primaryColor;
        cap = StrokeCap.round;
        break;
      case ElementRelationType.controlling:
      case ElementRelationType.controlled:
        lineColor = AppColors.secondaryColor;
        cap = StrokeCap.butt;
        break;
      case ElementRelationType.none:
      default:
        lineColor = Colors.grey;
        cap = StrokeCap.butt;
        break;
    }

    // 线条透明度随强度变化
    final opacity = (0.3 + strength * 0.7).clamp(0.0, 1.0);
    final color = lineColor.withAlpha((opacity * 255).toInt());

    // 线条宽度随强度变化
    final width = lineWidth * strength;

    return CustomPaint(
      size: Size(double.infinity, double.infinity),
      painter: _RelationLinePainter(
        start: start,
        end: end,
        color: color,
        width: width,
        cap: cap,
        hasArrow: hasArrow,
        relationType: relationType,
      ),
    );
  }
}

/// 五行关系线绘制器
class _RelationLinePainter extends CustomPainter {
  final Offset start;
  final Offset end;
  final Color color;
  final double width;
  final StrokeCap cap;
  final bool hasArrow;
  final ElementRelationType relationType;

  _RelationLinePainter({
    required this.start,
    required this.end,
    required this.color,
    required this.width,
    required this.cap,
    required this.hasArrow,
    required this.relationType,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = width
      ..strokeCap = cap
      ..style = PaintingStyle.stroke;

    // 画线
    canvas.drawLine(start, end, paint);

    // 如果需要绘制箭头
    if (hasArrow) {
      _drawArrow(canvas, start, end, relationType);
    }
  }

  void _drawArrow(Canvas canvas, Offset start, Offset end,
      ElementRelationType relationType) {
    // 检查是否有NaN值
    if (start.dx.isNaN || start.dy.isNaN || end.dx.isNaN || end.dy.isNaN) {
      // 防止NaN值导致渲染错误
      return;
    }

    final paint = Paint()
      ..color = _getRelationColor(relationType)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    // 计算方向向量
    final dx = end.dx - start.dx;
    final dy = end.dy - start.dy;
    final distance = math.sqrt(dx * dx + dy * dy);

    // 如果距离太小，不绘制箭头
    if (distance < 1e-10) {
      return;
    }

    // 单位向量
    final unitX = dx / distance;
    final unitY = dy / distance;

    // 箭头大小
    final arrowSize = math.max(width * 3, 6.0);

    // 箭头前端点位置 (调整一下，让箭头和线有一点距离)
    final tipX = end.dx - unitX * width;
    final tipY = end.dy - unitY * width;

    // 垂直于方向的单位向量
    final perpX = -unitY;
    final perpY = unitX;

    // 箭头的两个底角
    final leftX = tipX - unitX * arrowSize + perpX * arrowSize * 0.5;
    final leftY = tipY - unitY * arrowSize + perpY * arrowSize * 0.5;

    // 检查计算结果是否有NaN值
    if (leftX.isNaN || leftY.isNaN || tipX.isNaN || tipY.isNaN) {
      return;
    }

    final rightX = tipX - unitX * arrowSize - perpX * arrowSize * 0.5;
    final rightY = tipY - unitY * arrowSize - perpY * arrowSize * 0.5;

    // 检查右侧点是否有NaN值
    if (rightX.isNaN || rightY.isNaN) {
      return;
    }

    // 根据关系类型选择箭头样式
    if (relationType == ElementRelationType.generating ||
        relationType == ElementRelationType.generated) {
      // 生或被生关系，使用圆形箭头
      paint.style = PaintingStyle.fill;
      canvas.drawCircle(
        Offset(tipX, tipY),
        arrowSize * 0.5,
        paint,
      );
    } else {
      // 相克关系用三角形箭头
      final path = Path();
      path.moveTo(tipX, tipY);
      path.lineTo(leftX, leftY);
      path.lineTo(rightX, rightY);
      path.close();

      paint.style = PaintingStyle.fill;
      canvas.drawPath(path, paint);
    }
  }

  // 获取关系线颜色
  Color _getRelationColor(ElementRelationType relationType) {
    switch (relationType) {
      case ElementRelationType.generating:
      case ElementRelationType.generated:
        return AppColors.primaryColor;
      case ElementRelationType.controlling:
      case ElementRelationType.controlled:
        return AppColors.secondaryColor;
      case ElementRelationType.none:
      default:
        return Colors.grey;
    }
  }

  @override
  bool shouldRepaint(_RelationLinePainter oldDelegate) {
    return oldDelegate.start != start ||
        oldDelegate.end != end ||
        oldDelegate.color != color ||
        oldDelegate.width != width ||
        oldDelegate.cap != cap ||
        oldDelegate.hasArrow != hasArrow ||
        oldDelegate.relationType != relationType;
  }
}

/// 五行关系图组件
///
/// 展示五行元素之间的相生相克关系，支持多种布局方式
class FiveElementsChart extends StatefulWidget {
  /// 图表类型
  final FiveElementsChartType chartType;

  /// 是否显示相生关系
  final bool showGenerationCycle;

  /// 是否显示相克关系
  final bool showControlCycle;

  /// 五行数据
  final FiveElementsData data;

  /// 容器尺寸
  final double size;

  /// 元素尺寸
  final double elementSize;

  /// 是否启用动画
  final bool animated;

  /// 元素点击回调
  final Function(ElementType)? onElementTap;

  /// 构造函数
  const FiveElementsChart({
    Key? key,
    this.chartType = FiveElementsChartType.circular,
    this.showGenerationCycle = true,
    this.showControlCycle = false,
    required this.data,
    this.size = 300,
    this.elementSize = 50,
    this.animated = true,
    this.onElementTap,
  }) : super(key: key);

  @override
  State<FiveElementsChart> createState() => _FiveElementsChartState();
}

class _FiveElementsChartState extends State<FiveElementsChart>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();

    // 初始化动画
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );

    _animation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );

    if (widget.animated) {
      _animationController.forward();
    } else {
      _animationController.value = 1.0;
    }
  }

  @override
  void didUpdateWidget(FiveElementsChart oldWidget) {
    super.didUpdateWidget(oldWidget);

    // 当数据变化时重新执行动画
    if (oldWidget.data != widget.data) {
      if (widget.animated) {
        _animationController.reset();
        _animationController.forward();
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: AnimatedBuilder(
        animation: _animation,
        builder: (context, child) {
          return Stack(
            children: [
              // 绘制关系线
              if (widget.showGenerationCycle)
                ..._buildRelationLines(ElementRelationType.generating),

              if (widget.showControlCycle)
                ..._buildRelationLines(ElementRelationType.controlling),

              // 绘制元素节点
              ..._buildElementNodes(),
            ],
          );
        },
      ),
    );
  }

  // 根据图表类型获取元素位置
  Map<ElementType, Offset> _getElementPositions() {
    final center = Offset(widget.size / 2, widget.size / 2);
    final radius = (widget.size - widget.elementSize) / 2;
    final positions = <ElementType, Offset>{};

    switch (widget.chartType) {
      case FiveElementsChartType.circular:
        // 环形布局，元素分布在圆周上
        positions[ElementType.wood] =
            _getCircularPosition(center, radius, 90, _animation.value); // 上
        positions[ElementType.fire] =
            _getCircularPosition(center, radius, 162, _animation.value); // 右上
        positions[ElementType.earth] =
            _getCircularPosition(center, radius, 234, _animation.value); // 右下
        positions[ElementType.metal] =
            _getCircularPosition(center, radius, 306, _animation.value); // 左下
        positions[ElementType.water] =
            _getCircularPosition(center, radius, 18, _animation.value); // 左上
        break;

      case FiveElementsChartType.star:
        // 五角星布局
        positions[ElementType.wood] =
            _getCircularPosition(center, radius, 90, _animation.value); // 上
        positions[ElementType.fire] =
            _getCircularPosition(center, radius, 198, _animation.value); // 右下
        positions[ElementType.earth] =
            _getCircularPosition(center, radius, 306, _animation.value); // 左下
        positions[ElementType.metal] =
            _getCircularPosition(center, radius, 54, _animation.value); // 右上
        positions[ElementType.water] =
            _getCircularPosition(center, radius, 162, _animation.value); // 左上
        break;

      case FiveElementsChartType.linear:
        // 线性布局，元素水平排列
        final step = widget.size / 5;
        final yPos = center.dy;
        positions[ElementType.wood] =
            Offset(step * 0.5, yPos) * _animation.value;
        positions[ElementType.fire] =
            Offset(step * 1.5, yPos) * _animation.value;
        positions[ElementType.earth] =
            Offset(step * 2.5, yPos) * _animation.value;
        positions[ElementType.metal] =
            Offset(step * 3.5, yPos) * _animation.value;
        positions[ElementType.water] =
            Offset(step * 4.5, yPos) * _animation.value;
        break;
    }

    return positions;
  }

  // 获取环形布局中的位置
  Offset _getCircularPosition(
      Offset center, double radius, double angleDegrees, double animValue) {
    final angleRadians = angleDegrees * math.pi / 180;
    final x = center.dx + radius * math.cos(angleRadians) * animValue;
    final y = center.dy - radius * math.sin(angleRadians) * animValue;
    return Offset(x, y);
  }

  // 构建元素节点
  List<Widget> _buildElementNodes() {
    final positions = _getElementPositions();
    final nodes = <Widget>[];

    widget.data.values.forEach((element, value) {
      final position = positions[element]!;
      nodes.add(
        _ElementNode(
          elementType: element,
          size: widget.elementSize,
          value: value * _animation.value,
          position: position,
          enableBreathing: widget.animated,
          onTap: widget.onElementTap != null
              ? () => widget.onElementTap!(element)
              : null,
        ),
      );
    });

    return nodes;
  }

  // 构建关系线
  List<Widget> _buildRelationLines(ElementRelationType baseType) {
    final positions = _getElementPositions();
    final lines = <Widget>[];

    for (final relation in widget.data.relations) {
      // 过滤出指定类型的关系
      if (relation.type == baseType) {
        final start = positions[relation.source]!;
        final end = positions[relation.target]!;

        lines.add(
          _RelationLine(
            start: start,
            end: end,
            relationType: relation.type,
            strength: relation.strength * _animation.value,
            lineWidth: 2.0,
            hasArrow: true,
          ),
        );
      }
    }

    return lines;
  }
}
