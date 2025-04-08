import 'package:suoke_life/domain/entities/laoke/training_course.dart';

class TrainingCourseModel extends TrainingCourse {
  const TrainingCourseModel({
    required String id,
    required String title,
    required String description,
    required String content,
    required String instructorName,
    String? coverImageUrl,
    required int duration,
    required String level,
    required String categoryId,
    required String categoryName,
    required List<String> tags,
    required int studentsCount,
    required double rating,
    required int reviewsCount,
    required DateTime createdAt,
    required DateTime updatedAt,
    required List<CourseChapter> chapters,
  }) : super(
          id: id,
          title: title,
          description: description,
          content: content,
          instructorName: instructorName,
          coverImageUrl: coverImageUrl,
          duration: duration,
          level: level,
          categoryId: categoryId,
          categoryName: categoryName,
          tags: tags,
          studentsCount: studentsCount,
          rating: rating,
          reviewsCount: reviewsCount,
          createdAt: createdAt,
          updatedAt: updatedAt,
          chapters: chapters,
        );

  factory TrainingCourseModel.fromJson(Map<String, dynamic> json) {
    final List<CourseChapter> chapters = [];
    
    if (json['chapters'] != null) {
      for (var chapterJson in json['chapters']) {
        chapters.add(CourseChapterModel.fromJson(chapterJson));
      }
    }
    
    return TrainingCourseModel(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      content: json['content'] ?? '',
      instructorName: json['instructor_name'] ?? '',
      coverImageUrl: json['cover_image_url'],
      duration: json['duration'] ?? 0,
      level: json['level'] ?? '初级',
      categoryId: json['category_id'] ?? '',
      categoryName: json['category_name'] ?? '',
      tags: json['tags'] != null
          ? List<String>.from(json['tags'])
          : <String>[],
      studentsCount: json['students_count'] ?? 0,
      rating: (json['rating'] ?? 0.0).toDouble(),
      reviewsCount: json['reviews_count'] ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : DateTime.now(),
      chapters: chapters,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'content': content,
      'instructor_name': instructorName,
      'cover_image_url': coverImageUrl,
      'duration': duration,
      'level': level,
      'category_id': categoryId,
      'category_name': categoryName,
      'tags': tags,
      'students_count': studentsCount,
      'rating': rating,
      'reviews_count': reviewsCount,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'chapters': chapters.map((chapter) {
        if (chapter is CourseChapterModel) {
          return chapter.toJson();
        } else {
          // 在这种情况下，我们应该创建一个新的模型
          // 但这不应该经常发生，因为我们通常会使用模型类
          return {};
        }
      }).toList(),
    };
  }
}

class CourseChapterModel extends CourseChapter {
  const CourseChapterModel({
    required String id,
    required String title,
    required String description,
    required int duration,
    required int order,
    String? videoUrl,
    required bool isFree,
  }) : super(
          id: id,
          title: title,
          description: description,
          duration: duration,
          order: order,
          videoUrl: videoUrl,
          isFree: isFree,
        );

  factory CourseChapterModel.fromJson(Map<String, dynamic> json) {
    return CourseChapterModel(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      duration: json['duration'] ?? 0,
      order: json['order'] ?? 0,
      videoUrl: json['video_url'],
      isFree: json['is_free'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'duration': duration,
      'order': order,
      'video_url': videoUrl,
      'is_free': isFree,
    };
  }
} 