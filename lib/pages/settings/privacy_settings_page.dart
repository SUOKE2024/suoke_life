class PrivacySettingsPage extends GetView<PrivacyService> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('隐私设置')),
      body: ListView(
        children: [
          // 数据共享开关
          Obx(() => SwitchListTile(
            title: Text('参与数据共享'),
            subtitle: Text('贡献匿名数据用于改进AI模型'),
            value: controller.dataSharingEnabled.value,
            onChanged: controller.updateDataSharingConsent,
          )),
          
          // 数据导出
          ListTile(
            title: Text('导出个人数据'),
            trailing: Icon(Icons.download),
            onTap: controller.exportPersonalData,
          ),
          
          // 数据删除
          ListTile(
            title: Text('删除所有数据'),
            trailing: Icon(Icons.delete_forever),
            onTap: () => _showDeleteConfirmation(context),
          ),
        ],
      ),
    );
  }
} 