import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/group_permissions_controller.dart';
import '../../../core/base/base_page.dart';

class GroupPermissionsPage extends BasePage<GroupPermissionsController> {
  const GroupPermissionsPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('群聊权限'),
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return ListView(
      children: [
        // 成员权限
        Card(
          child: Column(
            children: [
              const ListTile(
                title: Text('成员权限'),
                subtitle: Text('设置群成员可以进行的操作'),
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('修改群名片'),
                trailing: Obx(() => Switch(
                      value: controller.canModifyAlias.value,
                      onChanged: controller.toggleModifyAlias,
                    )),
              ),
              ListTile(
                title: const Text('邀请新成员'),
                trailing: Obx(() => Switch(
                      value: controller.canInviteMembers.value,
                      onChanged: controller.toggleInviteMembers,
                    )),
              ),
              ListTile(
                title: const Text('查看群成员信息'),
                trailing: Obx(() => Switch(
                      value: controller.canViewMemberInfo.value,
                      onChanged: controller.toggleViewMemberInfo,
                    )),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 消息权限
        Card(
          child: Column(
            children: [
              const ListTile(
                title: Text('消息权限'),
                subtitle: Text('设置群成员发送消息的权限'),
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('发送消息'),
                trailing: Obx(() => Switch(
                      value: controller.canSendMessage.value,
                      onChanged: controller.toggleSendMessage,
                    )),
              ),
              ListTile(
                title: const Text('发送图片'),
                trailing: Obx(() => Switch(
                      value: controller.canSendImage.value,
                      onChanged: controller.toggleSendImage,
                    )),
              ),
              ListTile(
                title: const Text('发送文件'),
                trailing: Obx(() => Switch(
                      value: controller.canSendFile.value,
                      onChanged: controller.toggleSendFile,
                    )),
              ),
              ListTile(
                title: const Text('撤回消息'),
                trailing: Obx(() => Switch(
                      value: controller.canRecallMessage.value,
                      onChanged: controller.toggleRecallMessage,
                    )),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 管理权限
        Card(
          child: Column(
            children: [
              const ListTile(
                title: Text('管理权限'),
                subtitle: Text('设置管理员可以进行的操作'),
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('修改群资料'),
                trailing: Obx(() => Switch(
                      value: controller.canModifyGroupInfo.value,
                      onChanged: controller.toggleModifyGroupInfo,
                    )),
              ),
              ListTile(
                title: const Text('管理成员'),
                trailing: Obx(() => Switch(
                      value: controller.canManageMembers.value,
                      onChanged: controller.toggleManageMembers,
                    )),
              ),
              ListTile(
                title: const Text('设置管理员'),
                trailing: Obx(() => Switch(
                      value: controller.canSetAdmin.value,
                      onChanged: controller.toggleSetAdmin,
                    )),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
