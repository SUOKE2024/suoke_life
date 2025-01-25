import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'base_controller.dart';

abstract class BasePage<T extends BaseController> extends GetView<T> {
  const BasePage({Key? key}) : super(key: key);

  PreferredSizeWidget? buildAppBar(BuildContext context) {
    return null;
  }

  Widget buildBody(BuildContext context);

  Widget? buildFloatingActionButton(BuildContext context) {
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: buildAppBar(context),
      body: buildBody(context),
      floatingActionButton: buildFloatingActionButton(context),
    );
  }
} 