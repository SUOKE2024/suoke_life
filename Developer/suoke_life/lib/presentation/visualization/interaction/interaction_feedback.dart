import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/presentation/visualization/interaction/interaction_manager.dart';

class InteractionFeedback extends ConsumerWidget {
  final Widget child;

  const InteractionFeedback({
    super.key,
    required this.child,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final interactionState = ref.watch(interactionManagerProvider);

    return Stack(
      children: [
        // 主要内容
        child,

        // 交互反馈遮罩
        if (interactionState.isInteracting)
          _buildInteractionOverlay(context, interactionState),

        // 选中状态指示器
        if (interactionState.selectedNodeId != null || interactionState.selectedEdgeId != null)
          _buildSelectionIndicator(context, interactionState),

        // 高亮状态指示器
        if (interactionState.highlightedNodeIds.isNotEmpty || interactionState.highlightedEdgeIds.isNotEmpty)
          _buildHighlightIndicator(context, interactionState),
      ],
    );
  }

  Widget _buildInteractionOverlay(BuildContext context, InteractionState state) {
    final event = state.lastEvent;
    if (event == null) return const SizedBox.shrink();

    return CustomPaint(
      painter: InteractionPainter(
        event: event,
        color: Theme.of(context).primaryColor.withAlpha(50),
      ),
    );
  }

  Widget _buildSelectionIndicator(BuildContext context, InteractionState state) {
    return CustomPaint(
      painter: SelectionPainter(
        selectedNodeId: state.selectedNodeId,
        selectedEdgeId: state.selectedEdgeId,
        color: Theme.of(context).primaryColor,
      ),
    );
  }

  Widget _buildHighlightIndicator(BuildContext context, InteractionState state) {
    return CustomPaint(
      painter: HighlightPainter(
        highlightedNodeIds: state.highlightedNodeIds,
        highlightedEdgeIds: state.highlightedEdgeIds,
        color: Theme.of(context).colorScheme.secondary.withAlpha(128),
      ),
    );
  }
}

class InteractionPainter extends CustomPainter {
  final InteractionEvent event;
  final Color color;

  InteractionPainter({
    required this.event,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    switch (event.type) {
      case InteractionType.tap:
        _drawTapEffect(canvas, event.data, paint);
        break;
      case InteractionType.drag:
        _drawDragEffect(canvas, event.data, paint);
        break;
      case InteractionType.pinch:
        _drawPinchEffect(canvas, event.data, paint);
        break;
      case InteractionType.rotate:
        _drawRotateEffect(canvas, event.data, paint);
        break;
      default:
        break;
    }
  }

  void _drawTapEffect(Canvas canvas, Map<String, dynamic> data, Paint paint) {
    // 实现点击效果动画
  }

  void _drawDragEffect(Canvas canvas, Map<String, dynamic> data, Paint paint) {
    // 实现拖动效果动画
  }

  void _drawPinchEffect(Canvas canvas, Map<String, dynamic> data, Paint paint) {
    // 实现缩放效果动画
  }

  void _drawRotateEffect(Canvas canvas, Map<String, dynamic> data, Paint paint) {
    // 实现旋转效果动画
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class SelectionPainter extends CustomPainter {
  final String? selectedNodeId;
  final String? selectedEdgeId;
  final Color color;

  SelectionPainter({
    required this.selectedNodeId,
    required this.selectedEdgeId,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    if (selectedNodeId != null) {
      // 绘制节点选中效果
    }

    if (selectedEdgeId != null) {
      // 绘制边选中效果
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class HighlightPainter extends CustomPainter {
  final List<String> highlightedNodeIds;
  final List<String> highlightedEdgeIds;
  final Color color;

  HighlightPainter({
    required this.highlightedNodeIds,
    required this.highlightedEdgeIds,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    for (final nodeId in highlightedNodeIds) {
      // 绘制节点高亮效果
    }

    for (final edgeId in highlightedEdgeIds) {
      // 绘制边高亮效果
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}