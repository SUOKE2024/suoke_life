import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';

/// 获取博客文章详情用例
class GetBlogPostById implements UseCase<Map<String, dynamic>, BlogPostParams> {
  final LaokeRepository repository;

  GetBlogPostById(this.repository);

  @override
  Future<Either<Failure, Map<String, dynamic>>> call(BlogPostParams params) {
    return repository.getBlogPostById(params.id);
  }
}

/// 获取博客文章详情参数
class BlogPostParams extends Equatable {
  final String id;

  const BlogPostParams({required this.id});

  @override
  List<Object> get props => [id];
} 