import 'package:get/get.dart';
import '../../core/base/base_controller.dart';
import '../../data/models/group.dart';
import '../../data/models/group_member.dart';
import '../../services/group_service.dart';

class GroupManagementController extends BaseController {
  final _groupService = Get.find<GroupService>();
  final String groupId;

  final groupInfo = Group.empty().obs;
  final members = <GroupMember>[].obs;
  final inviteConfirmEnabled = false.obs;
  final muteAllEnabled = false.obs;

  bool get isOwner => 
      groupInfo.value.ownerId == Get.find<AuthService>().currentUser.value?.id;

  GroupManagementController({required this.groupId});

  @override
  void onInit() {
    super.onInit();
    _loadGroupInfo();
    _loadMembers();
    _loadSettings();
  }

  Future<void> _loadGroupInfo() async {
    try {
      final info = await _groupService.getGroupInfo(groupId);
      groupInfo.value = info;
    } catch (e) {
      showError('加载群信息失败');
    }
  }

  Future<void> _loadMembers() async {
    try {
      final list = await _groupService.getGroupMembers(groupId);
      members.value = list;
    } catch (e) {
      showError('加载成员列表失败');
    }
  }

  Future<void> _loadSettings() async {
    try {
      inviteConfirmEnabled.value = await _groupService.getInviteConfirmEnabled(groupId);
      muteAllEnabled.value = await _groupService.getMuteAllEnabled(groupId);
    } catch (e) {
      showError('加载群设置失败');
    }
  }

  void editGroupInfo() {
    Get.toNamed('/chat/group/edit', arguments: groupInfo.value);
  }

  void editAnnouncement() {
    Get.dialog(
      AlertDialog(
        title: const Text('编辑群公告'),
        content: TextField(
          maxLines: 5,
          decoration: const InputDecoration(
            hintText: '请输入群公告',
            border: OutlineInputBorder(),
          ),
          controller: TextEditingController(
            text: groupInfo.value.announcement,
          ),
          onSubmitted: (value) async {
            try {
              await _groupService.updateAnnouncement(groupId, value);
              groupInfo.update((val) {
                val?.announcement = value;
              });
              Get.back();
              showSuccess('群公告已更新');
            } catch (e) {
              showError('更新失败');
            }
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  Future<void> addMembers() async {
    final selected = await Get.toNamed<List<String>>('/contacts/select');
    if (selected != null && selected.isNotEmpty) {
      try {
        await _groupService.addMembers(groupId, selected);
        _loadMembers();
        showSuccess('添加成功');
      } catch (e) {
        showError('添加失败');
      }
    }
  }

  Future<void> changeMemberRole(GroupMember member, String role) async {
    try {
      await _groupService.changeMemberRole(groupId, member.userId, role);
      _loadMembers();
    } catch (e) {
      showError('修改失败');
    }
  }

  Future<void> removeMember(GroupMember member) async {
    try {
      await _groupService.removeMember(groupId, member.userId);
      members.removeWhere((m) => m.userId == member.userId);
    } catch (e) {
      showError('移除失败');
    }
  }

  Future<void> toggleInviteConfirm(bool value) async {
    try {
      await _groupService.setInviteConfirmEnabled(groupId, value);
      inviteConfirmEnabled.value = value;
    } catch (e) {
      showError('设置失败');
    }
  }

  Future<void> toggleMuteAll(bool value) async {
    try {
      await _groupService.setMuteAllEnabled(groupId, value);
      muteAllEnabled.value = value;
    } catch (e) {
      showError('设置失败');
    }
  }

  void showDisbandConfirmDialog() {
    Get.dialog(
      AlertDialog(
        title: const Text('解散群聊'),
        content: const Text('确定要解散该群聊吗？此操作不可恢复。'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Get.back();
              _disbandGroup();
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('解散'),
          ),
        ],
      ),
    );
  }

  Future<void> _disbandGroup() async {
    try {
      await _groupService.disbandGroup(groupId);
      Get.until((route) => route.isFirst);
      showSuccess('群聊已解散');
    } catch (e) {
      showError('解散失败');
    }
  }
} 