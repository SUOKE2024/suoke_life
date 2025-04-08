import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/data/datasources/remote/knowledge_remote_datasource.dart';
import 'package:suoke_life/data/repositories/knowledge_repository_impl.dart';
import 'package:suoke_life/domain/repositories/knowledge_repository.dart';
import 'package:suoke_life/domain/usecases/knowledge/get_nodes_usecase.dart';
import 'package:suoke_life/domain/usecases/knowledge/get_node_by_id_usecase.dart';
import 'package:suoke_life/domain/usecases/knowledge/get_node_relations_usecase.dart';
import 'package:suoke_life/domain/usecases/knowledge/search_nodes_usecase.dart';
import 'package:suoke_life/di/providers/api_providers.dart';

/// 知识远程数据源提供者
final knowledgeRemoteDataSourceProvider = Provider<KnowledgeRemoteDataSource>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return KnowledgeRemoteDataSourceImpl(apiClient);
});

/// 知识存储库提供者
final knowledgeRepositoryProvider = Provider<KnowledgeRepository>((ref) {
  final remoteDataSource = ref.watch(knowledgeRemoteDataSourceProvider);
  final networkInfo = ref.watch(networkInfoProvider);
  
  return KnowledgeRepositoryImpl(
    remoteDataSource: remoteDataSource,
    networkInfo: networkInfo,
  );
});

/// 获取知识节点列表用例提供者
final getNodesUseCaseProvider = Provider<GetNodesUseCase>((ref) {
  final repository = ref.watch(knowledgeRepositoryProvider);
  return GetNodesUseCase(repository);
});

/// 获取指定知识节点用例提供者
final getNodeByIdUseCaseProvider = Provider<GetNodeByIdUseCase>((ref) {
  final repository = ref.watch(knowledgeRepositoryProvider);
  return GetNodeByIdUseCase(repository);
});

/// 获取知识节点关系用例提供者
final getNodeRelationsUseCaseProvider = Provider<GetNodeRelationsUseCase>((ref) {
  final repository = ref.watch(knowledgeRepositoryProvider);
  return GetNodeRelationsUseCase(repository);
});

/// 搜索知识节点用例提供者
final searchNodesUseCaseProvider = Provider<SearchNodesUseCase>((ref) {
  final repository = ref.watch(knowledgeRepositoryProvider);
  return SearchNodesUseCase(repository);
});