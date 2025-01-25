import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life_app_app/features/life/services/life_record_service.dart';
import 'package:suoke_life_app_app/features/life/providers/life_record_provider.dart';
import 'package:suoke_life_app_app/features/life/models/life_record.dart';
import '../../../mocks.mocks.dart';

void main() {
  late LifeRecordProvider provider;
  late MockLifeRecordService mockService;

  setUp(() {
    mockService = MockLifeRecordService();
    provider = LifeRecordProvider();
    provider.service = mockService;
  });

  group('LifeRecordProvider Tests', () {
    final testRecord = LifeRecord(
      id: '1',
      title: '测试标题',
      content: '测试内容',
      createdAt: DateTime.now(),
      userId: 'test_user',
    );

    test('loadRecords should update records list', () async {
      when(mockService.getRecords('test_user'))
          .thenAnswer((_) async => [testRecord]);

      expect(provider.isLoading, false);
      expect(provider.records.isEmpty, true);

      await provider.loadRecords('test_user');

      expect(provider.isLoading, false);
      expect(provider.records.length, 1);
      expect(provider.records.first.id, '1');
      expect(provider.error, null);
    });

    test('loadRecords should handle errors', () async {
      when(mockService.getRecords('test_user'))
          .thenThrow(Exception('Test error'));

      await provider.loadRecords('test_user');

      expect(provider.isLoading, false);
      expect(provider.records.isEmpty, true);
      expect(provider.error, isNotNull);
    });

    test('addRecord should add record to list', () async {
      when(mockService.insertRecord(testRecord)).thenAnswer((_) async => {});

      await provider.addRecord(testRecord);

      expect(provider.records.length, 1);
      expect(provider.records.first.id, '1');
      expect(provider.error, null);
    });

    test('deleteRecord should remove record from list', () async {
      provider.records = [testRecord];
      when(mockService.deleteRecord('1')).thenAnswer((_) async => {});

      await provider.deleteRecord('1');

      expect(provider.records.isEmpty, true);
      expect(provider.error, null);
    });
  });
}
