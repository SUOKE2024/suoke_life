import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';

/// 获取博客文章列表用例
class GetBlogPosts implements UseCase<Map<String, dynamic>, BlogPostsParams> {
  final LaokeRepository repository;

  GetBlogPosts(this.repository);

  @override
  Future<Either<Failure, Map<String, dynamic>>> call(BlogPostsParams params) {
    return repository.getBlogPosts(
      authorId: params.authorId,
      categoryId: params.categoryId,
      tag: params.tag,
      status: params.status,
      page: params.page,
      limit: params.limit,
    );
  }
}

/// 获取博客文章列表参数
class BlogPostsParams extends Equatable {
  final String? authorId;
  final String? categoryId;
  final String? tag;
  final String? status;
  final int page;
  final int limit;

  const BlogPostsParams({
    this.authorId,
    this.categoryId,
    this.tag,
    this.status,
    this.page = 1,
    this.limit = 10,
  });

  @override
  List<Object?> get props => [authorId, categoryId, tag, status, page, limit];
} 