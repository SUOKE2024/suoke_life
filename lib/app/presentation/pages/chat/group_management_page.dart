import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/group_management_controller.dart';
import '../../../core/base/base_page.dart';
import '../../widgets/chat/member_list_item.dart';

class GroupManagementPage extends BasePage<GroupManagementController> {
  const GroupManagementPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('群聊管理'),
      actions: [
        IconButton(
          icon: const Icon(Icons.edit),
          onPressed: controller.editGroupInfo,
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return ListView(
      children: [
        // 群组信息
        Card(
          child: Column(
            children: [
              ListTile(
                leading: Obx(() => CircleAvatar(
                  backgroundImage: NetworkImage(controller.groupInfo.value.avatar),
                  radius: 24,
                )),
                title: Obx(() => Text(controller.groupInfo.value.name)),
                subtitle: Obx(() => Text('${controller.members.length}人')),
                trailing: const Icon(Icons.chevron_right),
                onTap: controller.editGroupInfo,
              ),
              ListTile(
                title: const Text('群公告'),
                subtitle: Obx(() => Text(
                  controller.groupInfo.value.announcement ?? '暂无公告',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                )),
                trailing: const Icon(Icons.chevron_right),
                onTap: controller.editAnnouncement,
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 群成员管理
        Card(
          child: Column(
            children: [
              ListTile(
                title: const Text('群成员管理'),
                trailing: TextButton(
                  onPressed: controller.addMembers,
                  child: const Text('添加'),
                ),
              ),
              const Divider(height: 1),
              Obx(() => ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: controller.members.length,
                itemBuilder: (context, index) {
                  final member = controller.members[index];
                  return MemberListItem(
                    member: member,
                    isOwner: controller.isOwner,
                    onRoleChanged: (role) => controller.changeMemberRole(member, role),
                    onRemove: () => controller.removeMember(member),
                  );
                },
              )),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 群设置
        Card(
          child: Column(
            children: [
              ListTile(
                title: const Text('群聊邀请确认'),
                subtitle: const Text('开启后，群成员需要群主或管理员确认才能邀请他人入群'),
                trailing: Obx(() => Switch(
                  value: controller.inviteConfirmEnabled.value,
                  onChanged: controller.toggleInviteConfirm,
                )),
              ),
              ListTile(
                title: const Text('全员禁言'),
                trailing: Obx(() => Switch(
                  value: controller.muteAllEnabled.value,
                  onChanged: controller.toggleMuteAll,
                )),
              ),
              ListTile(
                title: const Text('群聊权限'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.pushNamed('/chat/group/permissions'),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 解散群聊
        Card(
          child: ListTile(
            title: const Text(
              '解散群聊',
              style: TextStyle(color: Colors.red),
            ),
            onTap: controller.showDisbandConfirmDialog,
          ),
        ),
      ],
    );
  }
} 