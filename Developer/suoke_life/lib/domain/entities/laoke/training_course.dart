import 'package:equatable/equatable.dart';

/// 培训课程实体
class TrainingCourse extends Equatable {
  /// 唯一ID
  final String id;
  
  /// 课程标题
  final String title;
  
  /// 课程描述
  final String description;
  
  /// 课程内容
  final String content;
  
  /// 讲师名称
  final String instructorName;
  
  /// 课程封面图片URL
  final String? coverImageUrl;
  
  /// 课程时长（分钟）
  final int duration;
  
  /// 课程难度级别
  /// 初级、中级、高级
  final String level;
  
  /// 分类ID
  final String categoryId;
  
  /// 分类名称
  final String categoryName;
  
  /// 标签列表
  final List<String> tags;
  
  /// 学习人数
  final int studentsCount;
  
  /// 评分（1-5分）
  final double rating;
  
  /// 评价数量
  final int reviewsCount;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;
  
  /// 章节列表
  final List<CourseChapter> chapters;

  const TrainingCourse({
    required this.id,
    required this.title,
    required this.description,
    required this.content,
    required this.instructorName,
    this.coverImageUrl,
    required this.duration,
    required this.level,
    required this.categoryId,
    required this.categoryName,
    required this.tags,
    required this.studentsCount,
    required this.rating,
    required this.reviewsCount,
    required this.createdAt,
    required this.updatedAt,
    required this.chapters,
  });

  @override
  List<Object?> get props => [
        id,
        title,
        description,
        content,
        instructorName,
        coverImageUrl,
        duration,
        level,
        categoryId,
        categoryName,
        tags,
        studentsCount,
        rating,
        reviewsCount,
        createdAt,
        updatedAt,
        chapters,
      ];
}

/// 课程章节
class CourseChapter extends Equatable {
  /// 唯一ID
  final String id;
  
  /// 章节标题
  final String title;
  
  /// 章节描述
  final String description;
  
  /// 章节时长（分钟）
  final int duration;
  
  /// 章节序号
  final int order;
  
  /// 视频URL
  final String? videoUrl;
  
  /// 是否免费
  final bool isFree;

  const CourseChapter({
    required this.id,
    required this.title,
    required this.description,
    required this.duration,
    required this.order,
    this.videoUrl,
    required this.isFree,
  });

  @override
  List<Object?> get props => [
        id,
        title,
        description,
        duration,
        order,
        videoUrl,
        isFree,
      ];
} 