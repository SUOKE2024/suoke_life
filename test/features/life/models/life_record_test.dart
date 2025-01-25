import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life_app_app/features/life/models/life_record.dart';
import 'package:suoke_life_app_app/features/life/services/encryption_service.dart';

void main() {
  group('LifeRecord Tests', () {
    test('toMap should correctly encrypt sensitive data', () {
      final record = LifeRecord(
        id: '1',
        title: '测试标题',
        content: '测试内容',
        createdAt: DateTime.parse('2024-03-20'),
        userId: 'test_user',
        tags: ['tag1', 'tag2'],
        isPrivate: true,
      );

      final map = record.toMap();

      expect(map['id'], '1');
      expect(
        EncryptionService.decrypt(map['title']),
        '测试标题',
      );
      expect(
        EncryptionService.decrypt(map['content']),
        '测试内容',
      );
      expect(map['created_at'], '2024-03-20T00:00:00.000');
      expect(
        EncryptionService.decrypt(map['user_id']),
        'test_user',
      );
      expect(
        EncryptionService.decrypt(map['tags']),
        'tag1,tag2',
      );
      expect(map['is_private'], 1);
    });

    test('fromMap should correctly decrypt sensitive data', () {
      final map = {
        'id': '1',
        'title': EncryptionService.encrypt('测试标题'),
        'content': EncryptionService.encrypt('测试内容'),
        'created_at': '2024-03-20T00:00:00.000',
        'user_id': EncryptionService.encrypt('test_user'),
        'tags': EncryptionService.encrypt('tag1,tag2'),
        'is_private': 1,
      };

      final record = LifeRecord.fromMap(map);

      expect(record.id, '1');
      expect(record.title, '测试标题');
      expect(record.content, '测试内容');
      expect(record.createdAt, DateTime.parse('2024-03-20'));
      expect(record.userId, 'test_user');
      expect(record.tags, ['tag1', 'tag2']);
      expect(record.isPrivate, true);
    });
  });
}
