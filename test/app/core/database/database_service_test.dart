import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sqflite/sqflite.dart';
import 'package:suoke_app/app/core/database/database_service.dart';

class MockDatabase extends Mock implements Database {}

void main() {
  late DatabaseService databaseService;
  late MockDatabase mockDatabase;

  setUp(() {
    mockDatabase = MockDatabase();
    databaseService = DatabaseService(mockDatabase);
  });

  test('execute should call database execute', () async {
    const sql = 'SELECT * FROM test';
    when(() => mockDatabase.execute(sql)).thenAnswer((_) async {});

    await databaseService.execute(sql);

    verify(() => mockDatabase.execute(sql)).called(1);
  });
} 