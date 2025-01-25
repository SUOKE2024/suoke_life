import 'package:flutter/material.dart';

class ExpansionPanelItem {
  final String title;
  final Widget content;
  bool isExpanded;

  ExpansionPanelItem({
    required this.title,
    required this.content,
    this.isExpanded = false,
  });
}

class CustomExpansionPanelList extends StatefulWidget {
  final List<ExpansionPanelItem> items;
  final bool allowMultiple;
  final ValueChanged<int>? onExpansionChanged;

  const CustomExpansionPanelList({
    Key? key,
    required this.items,
    this.allowMultiple = false,
    this.onExpansionChanged,
  }) : super(key: key);

  @override
  State<CustomExpansionPanelList> createState() => _CustomExpansionPanelListState();
}

class _CustomExpansionPanelListState extends State<CustomExpansionPanelList> {
  @override
  Widget build(BuildContext context) {
    return ExpansionPanelList(
      expansionCallback: (index, isExpanded) {
        setState(() {
          if (!widget.allowMultiple) {
            // 如果不允许多个展开，先关闭其他面板
            for (var i = 0; i < widget.items.length; i++) {
              if (i != index) {
                widget.items[i].isExpanded = false;
              }
            }
          }
          widget.items[index].isExpanded = !isExpanded;
        });
        widget.onExpansionChanged?.call(index);
      },
      children: widget.items.map<ExpansionPanel>((item) {
        return ExpansionPanel(
          headerBuilder: (context, isExpanded) {
            return ListTile(
              title: Text(
                item.title,
                style: TextStyle(
                  fontWeight: isExpanded ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            );
          },
          body: Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: 16.0,
              vertical: 8.0,
            ),
            child: item.content,
          ),
          isExpanded: item.isExpanded,
          canTapOnHeader: true,
        );
      }).toList(),
    );
  }
}

// 使用示例：
class ExpansionPanelDemo extends StatelessWidget {
  final List<ExpansionPanelItem> items = [
    ExpansionPanelItem(
      title: '基本信息',
      content: Column(
        children: [
          ListTile(title: Text('姓名：张三')),
          ListTile(title: Text('年龄：25')),
          ListTile(title: Text('性别：男')),
        ],
      ),
    ),
    ExpansionPanelItem(
      title: '联系方式',
      content: Column(
        children: [
          ListTile(title: Text('电话：123456789')),
          ListTile(title: Text('邮箱：zhangsan@example.com')),
        ],
      ),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return CustomExpansionPanelList(
      items: items,
      allowMultiple: true,
      onExpansionChanged: (index) {
        print('Panel $index was toggled');
      },
    );
  }
} 