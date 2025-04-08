import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/data/datasources/remote/knowledge_graph_remote_datasource.dart';
import 'package:suoke_life/data/models/knowledge_graph_model.dart';
import 'package:suoke_life/domain/entities/knowledge_graph.dart';

class KnowledgeGraphSyncManager extends StateNotifier<AsyncValue<void>> {
  final IKnowledgeGraphRemoteDataSource _remoteDataSource;
  final Map<String, StreamController<KnowledgeGraphModel>> _syncControllers = {};
  Timer? _syncTimer;
  bool _isSyncing = false;

  KnowledgeGraphSyncManager(this._remoteDataSource) : super(const AsyncValue.data(null)) {
    _initializeSyncTimer();
  }

  void _initializeSyncTimer() {
    // 每5分钟执行一次同步
    _syncTimer = Timer.periodic(const Duration(minutes: 5), (_) {
      syncAll();
    });
  }

  Stream<KnowledgeGraphModel> subscribeToNodeUpdates(String nodeId) {
    if (!_syncControllers.containsKey(nodeId)) {
      final controller = StreamController<KnowledgeGraphModel>.broadcast();
      _syncControllers[nodeId] = controller;

      // 订阅远程更新
      _remoteDataSource.subscribeToUpdates(
        nodeId: nodeId,
        onUpdate: (update) {
          if (!controller.isClosed) {
            controller.add(update);
          }
        },
      );
    }

    return _syncControllers[nodeId]!.stream;
  }

  void unsubscribeFromNodeUpdates(String nodeId) {
    final controller = _syncControllers.remove(nodeId);
    if (controller != null) {
      controller.close();
      _remoteDataSource.unsubscribeFromUpdates(nodeId);
    }
  }

  Future<void> syncNode(String nodeId) async {
    if (_isSyncing) return;
    _isSyncing = true;

    try {
      state = const AsyncValue.loading();
      
      final graphData = await _remoteDataSource.getKnowledgeGraph(
        nodeId: nodeId,
        depth: 2,
      );

      final controller = _syncControllers[nodeId];
      if (controller != null && !controller.isClosed) {
        controller.add(graphData);
      }

      state = const AsyncValue.data(null);
    } on ServerException catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    } finally {
      _isSyncing = false;
    }
  }

  Future<void> syncAll() async {
    if (_isSyncing) return;
    _isSyncing = true;

    try {
      state = const AsyncValue.loading();
      
      for (final nodeId in _syncControllers.keys) {
        final graphData = await _remoteDataSource.getKnowledgeGraph(
          nodeId: nodeId,
          depth: 2,
        );

        final controller = _syncControllers[nodeId];
        if (controller != null && !controller.isClosed) {
          controller.add(graphData);
        }
      }

      state = const AsyncValue.data(null);
    } on ServerException catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    } finally {
      _isSyncing = false;
    }
  }

  Future<void> sendInteraction({
    required String nodeId,
    required String interactionType,
    Map<String, dynamic>? data,
  }) async {
    try {
      await _remoteDataSource.sendInteraction(
        nodeId: nodeId,
        interactionType: interactionType,
        data: data,
      );
    } on ServerException catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  @override
  void dispose() {
    _syncTimer?.cancel();
    for (final controller in _syncControllers.values) {
      controller.close();
    }
    _syncControllers.clear();
    super.dispose();
  }
}

final knowledgeGraphSyncManagerProvider =
    StateNotifierProvider<KnowledgeGraphSyncManager, AsyncValue<void>>((ref) {
  final remoteDataSource = ref.watch(knowledgeGraphRemoteDataSourceProvider);
  return KnowledgeGraphSyncManager(remoteDataSource);
});