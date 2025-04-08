import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/sync/knowledge_graph_sync_manager.dart';
import 'package:suoke_life/domain/entities/knowledge_graph.dart';

enum InteractionType {
  tap,
  doubleTap,
  longPress,
  drag,
  pinch,
  rotate,
  hover,
}

class InteractionEvent {
  final InteractionType type;
  final String targetId;
  final String targetType; // 'node' 或 'edge'
  final Map<String, dynamic> data;
  final DateTime timestamp;

  InteractionEvent({
    required this.type,
    required this.targetId,
    required this.targetType,
    required this.data,
  }) : timestamp = DateTime.now();

  Map<String, dynamic> toJson() => {
    'type': type.toString(),
    'targetId': targetId,
    'targetType': targetType,
    'data': data,
    'timestamp': timestamp.toIso8601String(),
  };
}

class InteractionState {
  final String? selectedNodeId;
  final String? selectedEdgeId;
  final List<String> highlightedNodeIds;
  final List<String> highlightedEdgeIds;
  final bool isInteracting;
  final InteractionEvent? lastEvent;

  const InteractionState({
    this.selectedNodeId,
    this.selectedEdgeId,
    this.highlightedNodeIds = const [],
    this.highlightedEdgeIds = const [],
    this.isInteracting = false,
    this.lastEvent,
  });

  InteractionState copyWith({
    String? selectedNodeId,
    String? selectedEdgeId,
    List<String>? highlightedNodeIds,
    List<String>? highlightedEdgeIds,
    bool? isInteracting,
    InteractionEvent? lastEvent,
  }) {
    return InteractionState(
      selectedNodeId: selectedNodeId ?? this.selectedNodeId,
      selectedEdgeId: selectedEdgeId ?? this.selectedEdgeId,
      highlightedNodeIds: highlightedNodeIds ?? this.highlightedNodeIds,
      highlightedEdgeIds: highlightedEdgeIds ?? this.highlightedEdgeIds,
      isInteracting: isInteracting ?? this.isInteracting,
      lastEvent: lastEvent ?? this.lastEvent,
    );
  }
}

class InteractionManager extends StateNotifier<InteractionState> {
  final KnowledgeGraphSyncManager _syncManager;
  final StreamController<InteractionEvent> _eventController = StreamController<InteractionEvent>.broadcast();
  Timer? _interactionTimer;

  InteractionManager(this._syncManager) : super(const InteractionState());

  Stream<InteractionEvent> get eventStream => _eventController.stream;

  void handleNodeInteraction(String nodeId, InteractionType type, [Map<String, dynamic>? data]) {
    final event = InteractionEvent(
      type: type,
      targetId: nodeId,
      targetType: 'node',
      data: data ?? {},
    );

    _processInteractionEvent(event);
  }

  void handleEdgeInteraction(String edgeId, InteractionType type, [Map<String, dynamic>? data]) {
    final event = InteractionEvent(
      type: type,
      targetId: edgeId,
      targetType: 'edge',
      data: data ?? {},
    );

    _processInteractionEvent(event);
  }

  void _processInteractionEvent(InteractionEvent event) {
    // 更新状态
    state = state.copyWith(
      isInteracting: true,
      lastEvent: event,
    );

    // 根据交互类型更新选中状态
    if (event.type == InteractionType.tap) {
      if (event.targetType == 'node') {
        state = state.copyWith(
          selectedNodeId: event.targetId,
          selectedEdgeId: null,
        );
      } else {
        state = state.copyWith(
          selectedEdgeId: event.targetId,
          selectedNodeId: null,
        );
      }
    }

    // 发送事件到流
    _eventController.add(event);

    // 发送到同步管理器
    _syncManager.sendInteraction(
      nodeId: event.targetId,
      interactionType: event.type.toString(),
      data: event.toJson(),
    );

    // 重置交互计时器
    _interactionTimer?.cancel();
    _interactionTimer = Timer(const Duration(milliseconds: 500), () {
      state = state.copyWith(isInteracting: false);
    });
  }

  void highlightNodes(List<String> nodeIds) {
    state = state.copyWith(highlightedNodeIds: nodeIds);
  }

  void highlightEdges(List<String> edgeIds) {
    state = state.copyWith(highlightedEdgeIds: edgeIds);
  }

  void clearHighlights() {
    state = state.copyWith(
      highlightedNodeIds: [],
      highlightedEdgeIds: [],
    );
  }

  void clearSelection() {
    state = state.copyWith(
      selectedNodeId: null,
      selectedEdgeId: null,
    );
  }

  @override
  void dispose() {
    _interactionTimer?.cancel();
    _eventController.close();
    super.dispose();
  }
}

final interactionManagerProvider =
    StateNotifierProvider<InteractionManager, InteractionState>((ref) {
  final syncManager = ref.watch(knowledgeGraphSyncManagerProvider.notifier);
  return InteractionManager(syncManager);
});