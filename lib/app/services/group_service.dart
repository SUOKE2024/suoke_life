import 'package:get/get.dart';
import '../data/models/group.dart';
import '../data/models/group_member.dart';
import '../core/network/api_client.dart';

class GroupService extends GetxService {
  final ApiClient _apiClient;
  
  GroupService({required ApiClient apiClient}) : _apiClient = apiClient;

  // 获取群组信息
  Future<Group> getGroupInfo(String groupId) async {
    try {
      final response = await _apiClient.get('/groups/$groupId');
      return Group.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }

  // 获取群成员列表
  Future<List<GroupMember>> getGroupMembers(String groupId) async {
    try {
      final response = await _apiClient.get('/groups/$groupId/members');
      return (response['members'] as List)
          .map((json) => GroupMember.fromJson(json))
          .toList();
    } catch (e) {
      rethrow;
    }
  }

  // 更新群组信息
  Future<void> updateGroupInfo(String groupId, {
    String? name,
    String? avatar,
    String? announcement,
  }) async {
    try {
      await _apiClient.put('/groups/$groupId', data: {
        if (name != null) 'name': name,
        if (avatar != null) 'avatar': avatar,
        if (announcement != null) 'announcement': announcement,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 添加群成员
  Future<void> addMembers(String groupId, List<String> userIds) async {
    try {
      await _apiClient.post('/groups/$groupId/members', data: {
        'userIds': userIds,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 移除群成员
  Future<void> removeMember(String groupId, String userId) async {
    try {
      await _apiClient.delete('/groups/$groupId/members/$userId');
    } catch (e) {
      rethrow;
    }
  }

  // 修改成员角色
  Future<void> changeMemberRole(String groupId, String userId, String role) async {
    try {
      await _apiClient.put('/groups/$groupId/members/$userId/role', data: {
        'role': role,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 禁言/解禁成员
  Future<void> toggleMemberMute(String groupId, String userId, bool mute) async {
    try {
      await _apiClient.put('/groups/$groupId/members/$userId/mute', data: {
        'muted': mute,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 获取群设置
  Future<Map<String, dynamic>> getGroupSettings(String groupId) async {
    try {
      final response = await _apiClient.get('/groups/$groupId/settings');
      return response['settings'];
    } catch (e) {
      rethrow;
    }
  }

  // 更新群设置
  Future<void> updateGroupSettings(String groupId, Map<String, dynamic> settings) async {
    try {
      await _apiClient.put('/groups/$groupId/settings', data: settings);
    } catch (e) {
      rethrow;
    }
  }

  // 获取邀请确认设置
  Future<bool> getInviteConfirmEnabled(String groupId) async {
    try {
      final settings = await getGroupSettings(groupId);
      return settings['inviteConfirmEnabled'] ?? false;
    } catch (e) {
      rethrow;
    }
  }

  // 设置邀请确认
  Future<void> setInviteConfirmEnabled(String groupId, bool enabled) async {
    try {
      await updateGroupSettings(groupId, {
        'inviteConfirmEnabled': enabled,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 获取全员禁言设置
  Future<bool> getMuteAllEnabled(String groupId) async {
    try {
      final settings = await getGroupSettings(groupId);
      return settings['muteAllEnabled'] ?? false;
    } catch (e) {
      rethrow;
    }
  }

  // 设置全员禁言
  Future<void> setMuteAllEnabled(String groupId, bool enabled) async {
    try {
      await updateGroupSettings(groupId, {
        'muteAllEnabled': enabled,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 解散群组
  Future<void> disbandGroup(String groupId) async {
    try {
      await _apiClient.delete('/groups/$groupId');
    } catch (e) {
      rethrow;
    }
  }

  // 退出群组
  Future<void> leaveGroup(String groupId) async {
    try {
      await _apiClient.post('/groups/$groupId/leave');
    } catch (e) {
      rethrow;
    }
  }

  // 转让群主
  Future<void> transferOwnership(String groupId, String newOwnerId) async {
    try {
      await _apiClient.post('/groups/$groupId/transfer', data: {
        'newOwnerId': newOwnerId,
      });
    } catch (e) {
      rethrow;
    }
  }
} 