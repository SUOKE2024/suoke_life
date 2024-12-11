import 'package:flutter/material.dart';

class DoNotDisturbPage extends StatefulWidget {
  const DoNotDisturbPage({super.key});

  @override
  State<DoNotDisturbPage> createState() => _DoNotDisturbPageState();
}

class _DoNotDisturbPageState extends State<DoNotDisturbPage> {
  bool _enabled = false;
  TimeOfDay _startTime = const TimeOfDay(hour: 22, minute: 0);
  TimeOfDay _endTime = const TimeOfDay(hour: 7, minute: 0);
  final List<bool> _weekdays = List.generate(7, (_) => true);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('免打扰时间'),
      ),
      body: ListView(
        children: [
          SwitchListTile(
            title: const Text('启用免打扰'),
            value: _enabled,
            onChanged: (value) {
              setState(() {
                _enabled = value;
              });
            },
          ),
          if (_enabled) ...[
            ListTile(
              title: const Text('开始时间'),
              trailing: Text(_startTime.format(context)),
              onTap: () async {
                final TimeOfDay? time = await showTimePicker(
                  context: context,
                  initialTime: _startTime,
                );
                if (time != null) {
                  setState(() {
                    _startTime = time;
                  });
                }
              },
            ),
            ListTile(
              title: const Text('结束时间'),
              trailing: Text(_endTime.format(context)),
              onTap: () async {
                final TimeOfDay? time = await showTimePicker(
                  context: context,
                  initialTime: _endTime,
                );
                if (time != null) {
                  setState(() {
                    _endTime = time;
                  });
                }
              },
            ),
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text('重复', style: TextStyle(fontWeight: FontWeight.bold)),
            ),
            Wrap(
              spacing: 8.0,
              children: [
                '周一',
                '周二',
                '周三',
                '周四',
                '周五',
                '周六',
                '周日',
              ].asMap().entries.map((entry) {
                final index = entry.key;
                final day = entry.value;
                return FilterChip(
                  label: Text(day),
                  selected: _weekdays[index],
                  onSelected: (bool selected) {
                    setState(() {
                      _weekdays[index] = selected;
                    });
                  },
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }
} 