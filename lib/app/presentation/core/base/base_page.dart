import 'package:flutter/material.dart';
import 'package:get/get.dart';

abstract class BasePage extends StatelessWidget {
  const BasePage({Key? key}) : super(key: key);

  // 页面标题
  String? get title => null;

  // 是否显示返回按钮
  bool get showBackButton => true;

  // 构建页面内容
  Widget buildBody(BuildContext context);

  // 构建AppBar
  PreferredSizeWidget? buildAppBar(BuildContext context) {
    if (title == null) return null;
    
    return AppBar(
      title: Text(title!),
      leading: showBackButton ? IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => Get.back(),
      ) : null,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: buildAppBar(context),
      body: buildBody(context),
    );
  }
} 