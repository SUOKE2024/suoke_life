import 'package:get/get.dart';
import '../../core/base/base_controller.dart';
import '../../services/group_service.dart';

class GroupPermissionsController extends BaseController {
  final _groupService = Get.find<GroupService>();
  final String groupId;

  // 成员权限
  final canModifyAlias = false.obs;
  final canInviteMembers = false.obs;
  final canViewMemberInfo = false.obs;

  // 消息权限
  final canSendMessage = true.obs;
  final canSendImage = true.obs;
  final canSendFile = true.obs;
  final canRecallMessage = true.obs;

  // 管理权限
  final canModifyGroupInfo = false.obs;
  final canManageMembers = false.obs;
  final canSetAdmin = false.obs;

  GroupPermissionsController({required this.groupId});

  @override
  void onInit() {
    super.onInit();
    _loadPermissions();
  }

  Future<void> _loadPermissions() async {
    try {
      final settings = await _groupService.getGroupSettings(groupId);
      final permissions = settings['permissions'] as Map<String, dynamic>;

      // 成员权限
      canModifyAlias.value = permissions['modifyAlias'] ?? false;
      canInviteMembers.value = permissions['inviteMembers'] ?? false;
      canViewMemberInfo.value = permissions['viewMemberInfo'] ?? false;

      // 消息权限
      canSendMessage.value = permissions['sendMessage'] ?? true;
      canSendImage.value = permissions['sendImage'] ?? true;
      canSendFile.value = permissions['sendFile'] ?? true;
      canRecallMessage.value = permissions['recallMessage'] ?? true;

      // 管理权限
      canModifyGroupInfo.value = permissions['modifyGroupInfo'] ?? false;
      canManageMembers.value = permissions['manageMembers'] ?? false;
      canSetAdmin.value = permissions['setAdmin'] ?? false;
    } catch (e) {
      showError('加载权限设置失败');
    }
  }

  Future<void> _updatePermission(String key, bool value) async {
    try {
      await _groupService.updateGroupSettings(groupId, {
        'permissions': {key: value},
      });
    } catch (e) {
      showError('更新权限失败');
      // 恢复原值
      switch (key) {
        case 'modifyAlias':
          canModifyAlias.value = !value;
          break;
        case 'inviteMembers':
          canInviteMembers.value = !value;
          break;
        case 'viewMemberInfo':
          canViewMemberInfo.value = !value;
          break;
        case 'sendMessage':
          canSendMessage.value = !value;
          break;
        case 'sendImage':
          canSendImage.value = !value;
          break;
        case 'sendFile':
          canSendFile.value = !value;
          break;
        case 'recallMessage':
          canRecallMessage.value = !value;
          break;
        case 'modifyGroupInfo':
          canModifyGroupInfo.value = !value;
          break;
        case 'manageMembers':
          canManageMembers.value = !value;
          break;
        case 'setAdmin':
          canSetAdmin.value = !value;
          break;
      }
    }
  }

  // 成员权限切换
  void toggleModifyAlias(bool value) => _updatePermission('modifyAlias', value);
  void toggleInviteMembers(bool value) => _updatePermission('inviteMembers', value);
  void toggleViewMemberInfo(bool value) => _updatePermission('viewMemberInfo', value);

  // 消息权限切换
  void toggleSendMessage(bool value) => _updatePermission('sendMessage', value);
  void toggleSendImage(bool value) => _updatePermission('sendImage', value);
  void toggleSendFile(bool value) => _updatePermission('sendFile', value);
  void toggleRecallMessage(bool value) => _updatePermission('recallMessage', value);

  // 管理权限切换
  void toggleModifyGroupInfo(bool value) => _updatePermission('modifyGroupInfo', value);
  void toggleManageMembers(bool value) => _updatePermission('manageMembers', value);
  void toggleSetAdmin(bool value) => _updatePermission('setAdmin', value);
} 