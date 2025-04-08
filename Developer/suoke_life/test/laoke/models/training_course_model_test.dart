import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/data/models/laoke/training_course_model.dart';
import 'package:suoke_life/domain/entities/laoke/training_course.dart';

void main() {
  final trainingCourseModel = TrainingCourseModel(
    id: '1',
    title: '中医基础理论入门',
    description: '本课程介绍中医基础理论知识，适合初学者',
    content: '详细的课程内容...',
    instructorName: '李老师',
    coverImageUrl: 'https://example.com/cover.jpg',
    duration: 120,
    level: '初级',
    categoryId: 'cat1',
    categoryName: '中医基础',
    tags: ['中医', '入门', '基础理论'],
    studentsCount: 100,
    rating: 4.5,
    reviewsCount: 20,
    createdAt: DateTime(2023, 1, 1),
    updatedAt: DateTime(2023, 1, 10),
    chapters: [
      CourseChapterModel(
        id: 'ch1',
        title: '第一章：中医基本概念',
        description: '介绍中医的基本概念和历史',
        duration: 30,
        order: 1,
        videoUrl: 'https://example.com/video1.mp4',
        isFree: true,
      ),
    ],
  );

  final Map<String, dynamic> jsonMap = {
    'id': '1',
    'title': '中医基础理论入门',
    'description': '本课程介绍中医基础理论知识，适合初学者',
    'content': '详细的课程内容...',
    'instructor_name': '李老师',
    'cover_image_url': 'https://example.com/cover.jpg',
    'duration': 120,
    'level': '初级',
    'category_id': 'cat1',
    'category_name': '中医基础',
    'tags': ['中医', '入门', '基础理论'],
    'students_count': 100,
    'rating': 4.5,
    'reviews_count': 20,
    'created_at': '2023-01-01T00:00:00.000',
    'updated_at': '2023-01-10T00:00:00.000',
    'chapters': [
      {
        'id': 'ch1',
        'title': '第一章：中医基本概念',
        'description': '介绍中医的基本概念和历史',
        'duration': 30,
        'order': 1,
        'video_url': 'https://example.com/video1.mp4',
        'is_free': true,
      }
    ],
  };

  group('TrainingCourseModel', () {
    test('应该是TrainingCourse的子类', () {
      // 验证
      expect(trainingCourseModel, isA<TrainingCourse>());
    });

    test('fromJson应该正确解析JSON', () {
      // 操作
      final result = TrainingCourseModel.fromJson(jsonMap);
      
      // 验证
      expect(result, equals(trainingCourseModel));
      expect(result.chapters.length, equals(1));
      expect(result.chapters.first, isA<CourseChapter>());
    });

    test('toJson应该正确转换为JSON', () {
      // 操作
      final result = trainingCourseModel.toJson();
      
      // 修正日期格式以匹配
      final expectedJson = Map<String, dynamic>.from(jsonMap);
      
      // 验证
      expect(result['id'], equals(expectedJson['id']));
      expect(result['title'], equals(expectedJson['title']));
      expect(result['instructor_name'], equals(expectedJson['instructor_name']));
      expect(result['chapters'].length, equals(expectedJson['chapters'].length));
    });

    test('处理缺少的字段', () {
      // 准备
      final incompleteJson = {
        'id': '2',
        'title': '中医诊断方法',
      };
      
      // 操作
      final result = TrainingCourseModel.fromJson(incompleteJson);
      
      // 验证
      expect(result.id, equals('2'));
      expect(result.title, equals('中医诊断方法'));
      expect(result.description, equals(''));
      expect(result.tags, isEmpty);
    });
  });
} 