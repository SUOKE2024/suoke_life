import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/domain/entities/laoke/knowledge_article.dart';
import 'package:suoke_life/domain/entities/laoke/knowledge_category.dart';

/// 老克服务存储库接口
abstract class LaokeRepository {
  /// 获取服务状态
  Future<Either<Failure, Map<String, dynamic>>> getServiceStatus();
  
  /// 获取知识分类列表
  Future<Either<Failure, List<KnowledgeCategory>>> getKnowledgeCategories();
  
  /// 获取知识文章列表
  Future<Either<Failure, Map<String, dynamic>>> getKnowledgeArticles({
    String? categoryId,
    int page = 1,
    int limit = 10,
  });
  
  /// 获取知识文章详情
  Future<Either<Failure, KnowledgeArticle>> getKnowledgeArticleById(String id);
  
  /// 获取培训课程列表
  Future<Either<Failure, Map<String, dynamic>>> getTrainingCourses({
    String? categoryId,
    String? level,
    int page = 1,
    int limit = 10,
  });
  
  /// 获取培训课程详情
  Future<Either<Failure, Map<String, dynamic>>> getTrainingCourseById(String id);
  
  /// 获取博客文章列表
  Future<Either<Failure, Map<String, dynamic>>> getBlogPosts({
    String? authorId,
    String? categoryId,
    String? tag,
    String? status,
    int page = 1,
    int limit = 10,
  });
  
  /// 获取博客文章详情
  Future<Either<Failure, Map<String, dynamic>>> getBlogPostById(String id);
  
  /// 文字转语音
  Future<Either<Failure, String>> textToSpeech(
    String text, {
    String? voiceId,
    Map<String, dynamic>? options,
  });
} 