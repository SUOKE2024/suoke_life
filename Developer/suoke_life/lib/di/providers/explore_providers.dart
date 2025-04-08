import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/data/datasources/remote/laoke_remote_datasource.dart';
import 'package:suoke_life/data/repositories/laoke_repository_impl.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';
import 'package:suoke_life/domain/usecases/laoke/get_knowledge_categories.dart';
import 'package:suoke_life/domain/usecases/laoke/get_knowledge_articles.dart';
import 'package:suoke_life/domain/usecases/laoke/get_knowledge_article_by_id.dart';
import 'package:suoke_life/domain/usecases/laoke/text_to_speech.dart';
import 'package:suoke_life/domain/usecases/laoke/get_training_courses.dart';
import 'package:suoke_life/domain/usecases/laoke/get_training_course_by_id.dart';
import 'package:suoke_life/domain/usecases/laoke/get_blog_posts.dart';
import 'package:suoke_life/domain/usecases/laoke/get_blog_post_by_id.dart';

/// 老克服务远程数据源提供者
final laokeRemoteDataSourceProvider = Provider<LaokeRemoteDataSource>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return LaokeRemoteDataSourceImpl(apiClient: apiClient);
});

/// 老克服务存储库提供者
final laokeRepositoryProvider = Provider<LaokeRepository>((ref) {
  final remoteDataSource = ref.watch(laokeRemoteDataSourceProvider);
  final networkInfo = ref.watch(networkInfoProvider);
  return LaokeRepositoryImpl(
    remoteDataSource: remoteDataSource,
    networkInfo: networkInfo,
  );
});

/// 获取知识分类用例提供者
final getKnowledgeCategoriesProvider = Provider<GetKnowledgeCategories>((ref) {
  final repository = ref.watch(laokeRepositoryProvider);
  return GetKnowledgeCategories(repository);
});

/// 获取知识文章列表用例提供者
final getKnowledgeArticlesProvider = Provider<GetKnowledgeArticles>((ref) {
  final repository = ref.watch(laokeRepositoryProvider);
  return GetKnowledgeArticles(repository);
});

/// 获取知识文章详情用例提供者
final getKnowledgeArticleByIdProvider = Provider<GetKnowledgeArticleById>((ref) {
  final repository = ref.watch(laokeRepositoryProvider);
  return GetKnowledgeArticleById(repository);
});

/// 获取培训课程列表用例提供者
final getTrainingCoursesProvider = Provider<GetTrainingCourses>((ref) {
  final repository = ref.watch(laokeRepositoryProvider);
  return GetTrainingCourses(repository);
});

/// 获取培训课程详情用例提供者
final getTrainingCourseByIdProvider = Provider<GetTrainingCourseById>((ref) {
  final repository = ref.watch(laokeRepositoryProvider);
  return GetTrainingCourseById(repository);
});

/// 获取博客文章列表用例提供者
final getBlogPostsProvider = Provider<GetBlogPosts>((ref) {
  final repository = ref.watch(laokeRepositoryProvider);
  return GetBlogPosts(repository);
});

/// 获取博客文章详情用例提供者
final getBlogPostByIdProvider = Provider<GetBlogPostById>((ref) {
  final repository = ref.watch(laokeRepositoryProvider);
  return GetBlogPostById(repository);
});

/// 文字转语音用例提供者
final textToSpeechProvider = Provider<TextToSpeech>((ref) {
  final repository = ref.watch(laokeRepositoryProvider);
  return TextToSpeech(repository);
});

/// 知识分类列表提供者
final knowledgeCategoriesProvider = FutureProvider((ref) async {
  final getKnowledgeCategories = ref.watch(getKnowledgeCategoriesProvider);
  final result = await getKnowledgeCategories();
  return result.fold(
    (failure) => throw Exception(failure.message),
    (categories) => categories,
  );
});

/// 知识文章列表状态
class KnowledgeArticlesState {
  final List<dynamic> articles;
  final int totalCount;
  final int currentPage;
  final int totalPages;
  final bool isLoading;
  final String? errorMessage;

  KnowledgeArticlesState({
    required this.articles,
    required this.totalCount,
    required this.currentPage,
    required this.totalPages,
    this.isLoading = false,
    this.errorMessage,
  });

  factory KnowledgeArticlesState.initial() {
    return KnowledgeArticlesState(
      articles: [],
      totalCount: 0,
      currentPage: 1,
      totalPages: 1,
      isLoading: true,
    );
  }

  KnowledgeArticlesState copyWith({
    List<dynamic>? articles,
    int? totalCount,
    int? currentPage,
    int? totalPages,
    bool? isLoading,
    String? errorMessage,
  }) {
    return KnowledgeArticlesState(
      articles: articles ?? this.articles,
      totalCount: totalCount ?? this.totalCount,
      currentPage: currentPage ?? this.currentPage,
      totalPages: totalPages ?? this.totalPages,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
    );
  }
}

/// 知识文章列表状态控制器
class KnowledgeArticlesNotifier extends StateNotifier<KnowledgeArticlesState> {
  final GetKnowledgeArticles getKnowledgeArticles;

  KnowledgeArticlesNotifier({required this.getKnowledgeArticles})
      : super(KnowledgeArticlesState.initial()) {
    fetchArticles();
  }

  Future<void> fetchArticles({String? categoryId, int page = 1, int limit = 10}) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    final result = await getKnowledgeArticles(
      KnowledgeArticlesParams(
        categoryId: categoryId,
        page: page,
        limit: limit,
      ),
    );

    result.fold(
      (failure) {
        state = state.copyWith(
          isLoading: false,
          errorMessage: failure.message,
        );
      },
      (data) {
        state = state.copyWith(
          articles: data['items'] ?? [],
          totalCount: data['total'] ?? 0,
          currentPage: data['page'] ?? 1,
          totalPages: data['total_pages'] ?? 1,
          isLoading: false,
        );
      },
    );
  }

  void refreshArticles({String? categoryId}) {
    fetchArticles(categoryId: categoryId, page: 1);
  }

  Future<void> loadMoreArticles({String? categoryId}) async {
    if (state.currentPage < state.totalPages && !state.isLoading) {
      final nextPage = state.currentPage + 1;
      
      state = state.copyWith(isLoading: true);
      
      final result = await getKnowledgeArticles(
        KnowledgeArticlesParams(
          categoryId: categoryId,
          page: nextPage,
          limit: 10,
        ),
      );
      
      result.fold(
        (failure) {
          state = state.copyWith(
            isLoading: false,
            errorMessage: failure.message,
          );
        },
        (data) {
          final newArticles = [...state.articles, ...(data['items'] ?? [])];
          state = state.copyWith(
            articles: newArticles,
            totalCount: data['total'] ?? 0,
            currentPage: data['page'] ?? state.currentPage,
            totalPages: data['total_pages'] ?? state.totalPages,
            isLoading: false,
          );
        },
      );
    }
  }
}

/// 知识文章列表提供者
final knowledgeArticlesProvider = StateNotifierProvider<KnowledgeArticlesNotifier, KnowledgeArticlesState>(
  (ref) => KnowledgeArticlesNotifier(
    getKnowledgeArticles: ref.watch(getKnowledgeArticlesProvider),
  ),
);

/// 培训课程列表状态
class TrainingCoursesState {
  final List<dynamic> courses;
  final int totalCount;
  final int currentPage;
  final int totalPages;
  final bool isLoading;
  final String? errorMessage;

  TrainingCoursesState({
    required this.courses,
    required this.totalCount,
    required this.currentPage,
    required this.totalPages,
    this.isLoading = false,
    this.errorMessage,
  });

  factory TrainingCoursesState.initial() {
    return TrainingCoursesState(
      courses: [],
      totalCount: 0,
      currentPage: 1,
      totalPages: 1,
      isLoading: true,
    );
  }

  TrainingCoursesState copyWith({
    List<dynamic>? courses,
    int? totalCount,
    int? currentPage,
    int? totalPages,
    bool? isLoading,
    String? errorMessage,
  }) {
    return TrainingCoursesState(
      courses: courses ?? this.courses,
      totalCount: totalCount ?? this.totalCount,
      currentPage: currentPage ?? this.currentPage,
      totalPages: totalPages ?? this.totalPages,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
    );
  }
}

/// 培训课程列表状态控制器
class TrainingCoursesNotifier extends StateNotifier<TrainingCoursesState> {
  final GetTrainingCourses getTrainingCourses;
  
  TrainingCoursesNotifier({required this.getTrainingCourses}) 
      : super(TrainingCoursesState.initial());
  
  Future<void> fetchCourses({String? categoryId, String? level, int page = 1, int limit = 10}) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    
    final params = TrainingCoursesParams(
      categoryId: categoryId,
      level: level,
      page: page,
      limit: limit
    );
    
    final result = await getTrainingCourses(params);
    
    result.fold(
      (failure) => state = state.copyWith(
        isLoading: false,
        errorMessage: failure.message,
      ),
      (data) {
        state = state.copyWith(
          isLoading: false,
          courses: data['items'],
          totalCount: data['total'],
          currentPage: data['page'],
          totalPages: data['total_pages'],
        );
      }
    );
  }

  void refreshCourses({String? categoryId, String? level}) {
    fetchCourses(categoryId: categoryId, level: level, page: 1);
  }

  Future<void> loadMoreCourses({String? categoryId, String? level}) async {
    if (state.currentPage < state.totalPages && !state.isLoading) {
      final nextPage = state.currentPage + 1;
      
      state = state.copyWith(isLoading: true);
      
      final result = await getTrainingCourses(
        TrainingCoursesParams(
          categoryId: categoryId,
          level: level,
          page: nextPage,
          limit: 10,
        ),
      );
      
      result.fold(
        (failure) {
          state = state.copyWith(
            isLoading: false,
            errorMessage: failure.message,
          );
        },
        (data) {
          final newCourses = [...state.courses, ...(data['items'] ?? [])];
          state = state.copyWith(
            courses: newCourses,
            totalCount: data['total'] ?? 0,
            currentPage: data['page'] ?? state.currentPage,
            totalPages: data['total_pages'] ?? state.totalPages,
            isLoading: false,
          );
        },
      );
    }
  }
}

/// 培训课程列表提供者
final trainingCoursesProvider = StateNotifierProvider<TrainingCoursesNotifier, TrainingCoursesState>(
  (ref) => TrainingCoursesNotifier(
    getTrainingCourses: ref.watch(getTrainingCoursesProvider),
  ),
);

/// 博客文章列表状态
class BlogPostsState {
  final List<dynamic> posts;
  final int totalCount;
  final int currentPage;
  final int totalPages;
  final bool isLoading;
  final String? errorMessage;

  BlogPostsState({
    required this.posts,
    required this.totalCount,
    required this.currentPage,
    required this.totalPages,
    this.isLoading = false,
    this.errorMessage,
  });

  factory BlogPostsState.initial() {
    return BlogPostsState(
      posts: [],
      totalCount: 0,
      currentPage: 1,
      totalPages: 1,
      isLoading: true,
    );
  }

  BlogPostsState copyWith({
    List<dynamic>? posts,
    int? totalCount,
    int? currentPage,
    int? totalPages,
    bool? isLoading,
    String? errorMessage,
  }) {
    return BlogPostsState(
      posts: posts ?? this.posts,
      totalCount: totalCount ?? this.totalCount,
      currentPage: currentPage ?? this.currentPage,
      totalPages: totalPages ?? this.totalPages,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
    );
  }
}

/// 博客文章列表状态控制器
class BlogPostsNotifier extends StateNotifier<BlogPostsState> {
  final GetBlogPosts getBlogPosts;
  
  BlogPostsNotifier({required this.getBlogPosts}) 
      : super(BlogPostsState.initial());
  
  Future<void> fetchPosts({String? authorId, String? categoryId, String? tag, String? status, int page = 1, int limit = 10}) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    
    final params = BlogPostsParams(
      authorId: authorId,
      categoryId: categoryId,
      tag: tag,
      status: status,
      page: page,
      limit: limit
    );
    
    final result = await getBlogPosts(params);
    
    result.fold(
      (failure) => state = state.copyWith(
        isLoading: false,
        errorMessage: failure.message,
      ),
      (data) {
        state = state.copyWith(
          isLoading: false,
          posts: data['items'],
          totalCount: data['total'],
          currentPage: data['page'],
          totalPages: data['total_pages'],
        );
      }
    );
  }

  void refreshPosts({
    String? authorId,
    String? categoryId,
    String? tag,
    String? status,
  }) {
    fetchPosts(
      authorId: authorId,
      categoryId: categoryId,
      tag: tag,
      status: status,
      page: 1,
    );
  }

  Future<void> loadMorePosts({
    String? authorId,
    String? categoryId,
    String? tag,
    String? status,
  }) async {
    if (state.currentPage < state.totalPages && !state.isLoading) {
      final nextPage = state.currentPage + 1;
      
      state = state.copyWith(isLoading: true);
      
      final result = await getBlogPosts(
        BlogPostsParams(
          authorId: authorId,
          categoryId: categoryId,
          tag: tag,
          status: status,
          page: nextPage,
          limit: 10,
        ),
      );
      
      result.fold(
        (failure) {
          state = state.copyWith(
            isLoading: false,
            errorMessage: failure.message,
          );
        },
        (data) {
          final newPosts = [...state.posts, ...(data['items'] ?? [])];
          state = state.copyWith(
            posts: newPosts,
            totalCount: data['total'] ?? 0,
            currentPage: data['page'] ?? state.currentPage,
            totalPages: data['total_pages'] ?? state.totalPages,
            isLoading: false,
          );
        },
      );
    }
  }
}

/// 博客文章列表提供者
final blogPostsProvider = StateNotifierProvider<BlogPostsNotifier, BlogPostsState>(
  (ref) => BlogPostsNotifier(
    getBlogPosts: ref.watch(getBlogPostsProvider),
  ),
);