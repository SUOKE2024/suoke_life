import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/data/models/knowledge_model.dart';

/// 知识存储库接口
abstract class KnowledgeRepository {
  /// 获取知识节点列表
  Future<Either<Failure, List<KnowledgeNodeModel>>> getNodes({
    String? query,
    List<String>? tags,
    List<String>? types,
    int page = 1,
    int pageSize = 20
  });
  
  /// 获取指定知识节点
  Future<Either<Failure, KnowledgeNodeModel>> getNodeById(String nodeId);
  
  /// 获取知识节点关系
  Future<Either<Failure, List<KnowledgeRelationModel>>> getNodeRelations(String nodeId);
  
  /// 搜索知识节点
  Future<Either<Failure, List<KnowledgeNodeModel>>> searchNodes(String query);
} 