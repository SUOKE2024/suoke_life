import '../data/local/database/app_database.dart';
import '../data/remote/mysql/knowledge_database.dart';
import 'encryption_service.dart';

class UserService {
  final AppDatabase _localDb;
  final KnowledgeDatabase _knowledgeDb;
  final EncryptionService _encryptionService;

  UserService(this._localDb, this._knowledgeDb, this._encryptionService);

  // 用户画像管理
  Future<void> updateUserProfile(String userId, Map<String, dynamic> profile) async {
    // 加密敏感信息
    if (profile['health_data'] != null) {
      profile['health_data'] = _encryptionService.encryptByLevel(
        jsonEncode(profile['health_data']),
        SecurityLevel.S0,
      );
    }

    await _localDb.database.then((db) => db.insert(
      'user_profiles',
      {
        'user_id': userId,
        'profile_data': jsonEncode(profile),
        'updated_at': DateTime.now().millisecondsSinceEpoch,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    ));
  }

  // 专家认证
  Future<void> applyExpertVerification(
    String userId,
    Map<String, dynamic> credentials,
  ) async {
    await _knowledgeDb._conn.query('''
      INSERT INTO expert_verifications (
        id, user_id, credentials, status, created_at
      ) VALUES (?, ?, ?, ?, NOW())
    ''', [
      DateTime.now().millisecondsSinceEpoch.toString(),
      userId,
      jsonEncode(credentials),
      'pending',
    ]);
  }

  // 会员管理
  Future<void> updateMembership(String userId, String membershipType) async {
    await _knowledgeDb._conn.query('''
      INSERT INTO user_memberships (
        user_id, type, start_date, end_date
      ) VALUES (?, ?, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR))
      ON DUPLICATE KEY UPDATE
        type = VALUES(type),
        start_date = VALUES(start_date),
        end_date = VALUES(end_date)
    ''', [userId, membershipType]);
  }

  // 角色管理
  Future<List<String>> getUserRoles(String userId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT role_type FROM user_roles WHERE user_id = ?
    ''', [userId]);
    
    return results.map((r) => r['role_type'] as String).toList();
  }
} 