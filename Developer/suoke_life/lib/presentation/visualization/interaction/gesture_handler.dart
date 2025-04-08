import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/presentation/visualization/interaction/interaction_manager.dart';

class GestureHandler extends ConsumerStatefulWidget {
  final Widget child;
  final String? targetId;
  final String targetType;
  final bool enablePanAndScale;
  final bool enableRotation;
  final VoidCallback? onTap;

  const GestureHandler({
    super.key,
    required this.child,
    this.targetId,
    this.targetType = 'node',
    this.enablePanAndScale = true,
    this.enableRotation = true,
    this.onTap,
  });

  @override
  ConsumerState<GestureHandler> createState() => _GestureHandlerState();
}

class _GestureHandlerState extends ConsumerState<GestureHandler> {
  Offset _lastFocalPoint = Offset.zero;
  double _lastScale = 1.0;
  double _lastRotation = 0.0;
  bool _isDragging = false;

  void _handleTap() {
    if (widget.targetId != null) {
      if (widget.targetType == 'node') {
        ref.read(interactionManagerProvider.notifier).handleNodeInteraction(
          widget.targetId!,
          InteractionType.tap,
        );
      } else {
        ref.read(interactionManagerProvider.notifier).handleEdgeInteraction(
          widget.targetId!,
          InteractionType.tap,
        );
      }
    }
    widget.onTap?.call();
  }

  void _handleDoubleTap() {
    if (widget.targetId != null) {
      if (widget.targetType == 'node') {
        ref.read(interactionManagerProvider.notifier).handleNodeInteraction(
          widget.targetId!,
          InteractionType.doubleTap,
        );
      } else {
        ref.read(interactionManagerProvider.notifier).handleEdgeInteraction(
          widget.targetId!,
          InteractionType.doubleTap,
        );
      }
    }
  }

  void _handleLongPress() {
    if (widget.targetId != null) {
      if (widget.targetType == 'node') {
        ref.read(interactionManagerProvider.notifier).handleNodeInteraction(
          widget.targetId!,
          InteractionType.longPress,
        );
      } else {
        ref.read(interactionManagerProvider.notifier).handleEdgeInteraction(
          widget.targetId!,
          InteractionType.longPress,
        );
      }
    }
  }

  void _handleScaleStart(ScaleStartDetails details) {
    _lastFocalPoint = details.focalPoint;
    _lastScale = 1.0;
    _lastRotation = 0.0;
    _isDragging = false;
  }

  void _handleScaleUpdate(ScaleUpdateDetails details) {
    if (!widget.enablePanAndScale) return;

    final delta = details.focalPoint - _lastFocalPoint;
    _lastFocalPoint = details.focalPoint;

    // 处理拖动
    if (details.scale == 1.0 && !_isDragging && delta.distance > 5.0) {
      _isDragging = true;
    }

    if (_isDragging && widget.targetId != null) {
      if (widget.targetType == 'node') {
        ref.read(interactionManagerProvider.notifier).handleNodeInteraction(
          widget.targetId!,
          InteractionType.drag,
          {'delta': {'x': delta.dx, 'y': delta.dy}},
        );
      } else {
        ref.read(interactionManagerProvider.notifier).handleEdgeInteraction(
          widget.targetId!,
          InteractionType.drag,
          {'delta': {'x': delta.dx, 'y': delta.dy}},
        );
      }
    }

    // 处理缩放
    if (details.scale != 1.0 && widget.targetId != null) {
      final scaleDelta = details.scale / _lastScale;
      _lastScale = details.scale;

      if (widget.targetType == 'node') {
        ref.read(interactionManagerProvider.notifier).handleNodeInteraction(
          widget.targetId!,
          InteractionType.pinch,
          {'scale': scaleDelta},
        );
      } else {
        ref.read(interactionManagerProvider.notifier).handleEdgeInteraction(
          widget.targetId!,
          InteractionType.pinch,
          {'scale': scaleDelta},
        );
      }
    }

    // 处理旋转
    if (widget.enableRotation && details.rotation != 0.0 && widget.targetId != null) {
      final rotationDelta = details.rotation - _lastRotation;
      _lastRotation = details.rotation;

      if (widget.targetType == 'node') {
        ref.read(interactionManagerProvider.notifier).handleNodeInteraction(
          widget.targetId!,
          InteractionType.rotate,
          {'rotation': rotationDelta},
        );
      } else {
        ref.read(interactionManagerProvider.notifier).handleEdgeInteraction(
          widget.targetId!,
          InteractionType.rotate,
          {'rotation': rotationDelta},
        );
      }
    }
  }

  void _handleHover(PointerHoverEvent event) {
    if (widget.targetId != null) {
      if (widget.targetType == 'node') {
        ref.read(interactionManagerProvider.notifier).handleNodeInteraction(
          widget.targetId!,
          InteractionType.hover,
          {'position': {'x': event.position.dx, 'y': event.position.dy}},
        );
      } else {
        ref.read(interactionManagerProvider.notifier).handleEdgeInteraction(
          widget.targetId!,
          InteractionType.hover,
          {'position': {'x': event.position.dx, 'y': event.position.dy}},
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onHover: _handleHover,
      child: GestureDetector(
        onTap: _handleTap,
        onDoubleTap: _handleDoubleTap,
        onLongPress: _handleLongPress,
        onScaleStart: _handleScaleStart,
        onScaleUpdate: _handleScaleUpdate,
        child: widget.child,
      ),
    );
  }
}