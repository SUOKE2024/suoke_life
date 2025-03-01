import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/knowledge_node.dart';
import '../../domain/entities/knowledge_relation.dart';
import '../../domain/repositories/knowledge_graph_repository.dart';
import '../../di/providers.dart';

/// 知识图谱主题过滤器Provider
final knowledgeGraphFilterProvider = StateProvider<String>((ref) => '全部');

/// 知识图谱缩放级别Provider
final knowledgeGraphZoomLevelProvider = StateProvider<double>((ref) => 1.0);

/// 选中主题Provider
final selectedTopicProvider = StateProvider<String>((ref) => '中医养生');

/// 知识图谱节点Provider
final knowledgeNodesProvider = FutureProvider<List<KnowledgeNode>>((ref) {
  final knowledgeGraphRepository = ref.watch(knowledgeGraphRepositoryProvider);
  final topic = ref.watch(selectedTopicProvider);
  final filter = ref.watch(knowledgeGraphFilterProvider);
  
  return knowledgeGraphRepository.getNodes(topic: topic, filter: filter);
});

/// 知识图谱关系Provider
final knowledgeRelationsProvider = FutureProvider<List<KnowledgeRelation>>((ref) {
  final knowledgeGraphRepository = ref.watch(knowledgeGraphRepositoryProvider);
  final nodes = ref.watch(knowledgeNodesProvider).value ?? [];
  
  if (nodes.isEmpty) {
    return [];
  }
  
  // 获取所有节点ID
  final nodeIds = nodes.map((node) => node.id).toSet();
  
  return knowledgeGraphRepository.getRelations(nodeIds: nodeIds);
});

/// 选中节点Provider
final selectedNodeProvider = StateProvider<KnowledgeNode?>((ref) => null);

/// 知识图谱存储库Provider
final knowledgeGraphRepositoryProvider = Provider<KnowledgeGraphRepository>((ref) {
  final databaseHelper = ref.watch(databaseHelperProvider);
  return LocalKnowledgeGraphRepository(databaseHelper);
});

/// 知识图谱布局类型
enum KnowledgeGraphLayoutType {
  force,     // 力导向布局
  radial,    // 放射状布局
  hierarchy, // 层次结构布局
  circular   // 环形布局
}

/// 布局类型Provider
final layoutTypeProvider = StateProvider<KnowledgeGraphLayoutType>((ref) {
  return KnowledgeGraphLayoutType.force;
});

/// 知识图谱控制器Notifier
class KnowledgeGraphControllerNotifier extends StateNotifier<KnowledgeGraphControllerState> {
  final Ref ref;
  
  KnowledgeGraphControllerNotifier(this.ref) : super(KnowledgeGraphControllerState(
    layoutType: ref.read(layoutTypeProvider),
    zoomLevel: ref.read(knowledgeGraphZoomLevelProvider),
    filter: ref.read(knowledgeGraphFilterProvider),
    selectedTopic: ref.read(selectedTopicProvider),
    selectedNode: ref.read(selectedNodeProvider),
  ));
  
  /// 设置布局类型
  void setLayoutType(KnowledgeGraphLayoutType type) {
    ref.read(layoutTypeProvider.notifier).state = type;
    state = state.copyWith(layoutType: type);
  }
  
  /// 设置缩放级别
  void setZoomLevel(double zoomLevel) {
    if (zoomLevel < 0.5) zoomLevel = 0.5;
    if (zoomLevel > 2.0) zoomLevel = 2.0;
    
    ref.read(knowledgeGraphZoomLevelProvider.notifier).state = zoomLevel;
    state = state.copyWith(zoomLevel: zoomLevel);
  }
  
  /// 设置过滤器
  void setFilter(String filter) {
    ref.read(knowledgeGraphFilterProvider.notifier).state = filter;
    state = state.copyWith(filter: filter);
  }
  
  /// 选择主题
  void selectTopic(String topic) {
    ref.read(selectedTopicProvider.notifier).state = topic;
    state = state.copyWith(selectedTopic: topic);
  }
  
  /// 选择节点
  void selectNode(KnowledgeNode? node) {
    ref.read(selectedNodeProvider.notifier).state = node;
    state = state.copyWith(selectedNode: node);
  }
  
  /// 刷新图谱
  Future<void> refreshGraph() async {
    state = state.copyWith(isRefreshing: true);
    
    // 触发重新获取数据
    ref.invalidate(knowledgeNodesProvider);
    ref.invalidate(knowledgeRelationsProvider);
    
    // 短暂延迟以确保UI更新
    await Future.delayed(const Duration(milliseconds: 300));
    
    state = state.copyWith(isRefreshing: false);
  }
}

/// 知识图谱控制器状态
class KnowledgeGraphControllerState {
  final KnowledgeGraphLayoutType layoutType;
  final double zoomLevel;
  final String filter;
  final String selectedTopic;
  final KnowledgeNode? selectedNode;
  final bool isRefreshing;
  
  KnowledgeGraphControllerState({
    this.layoutType = KnowledgeGraphLayoutType.force,
    this.zoomLevel = 1.0,
    this.filter = '全部',
    this.selectedTopic = '中医养生',
    this.selectedNode,
    this.isRefreshing = false,
  });
  
  KnowledgeGraphControllerState copyWith({
    KnowledgeGraphLayoutType? layoutType,
    double? zoomLevel,
    String? filter,
    String? selectedTopic,
    KnowledgeNode? selectedNode,
    bool? isRefreshing,
  }) {
    return KnowledgeGraphControllerState(
      layoutType: layoutType ?? this.layoutType,
      zoomLevel: zoomLevel ?? this.zoomLevel,
      filter: filter ?? this.filter,
      selectedTopic: selectedTopic ?? this.selectedTopic,
      selectedNode: selectedNode ?? this.selectedNode,
      isRefreshing: isRefreshing ?? this.isRefreshing,
    );
  }
}

/// 知识图谱控制器Provider
final knowledgeGraphControllerProvider = StateNotifierProvider<KnowledgeGraphControllerNotifier, KnowledgeGraphControllerState>(
  (ref) => KnowledgeGraphControllerNotifier(ref),
); 