import 'package:flutter/material.dart';

class DoctorInfo {
  final String id;
  final String name;
  final String title;
  final String department;
  final String? avatar;
  final List<String> expertise;
  final double rating;
  final bool isAvailable;

  DoctorInfo({
    required this.id,
    required this.name,
    required this.title,
    required this.department,
    this.avatar,
    required this.expertise,
    required this.rating,
    this.isAvailable = true,
  });
}

class DoctorSelector extends StatefulWidget {
  final List<String> selectedDoctors;
  final ValueChanged<List<String>> onChanged;

  const DoctorSelector({
    Key? key,
    required this.selectedDoctors,
    required this.onChanged,
  }) : super(key: key);

  @override
  _DoctorSelectorState createState() => _DoctorSelectorState();
}

class _DoctorSelectorState extends State<DoctorSelector> {
  final List<DoctorInfo> _doctors = [
    // TODO: 从服务获取医生列表
    DoctorInfo(
      id: '1',
      name: '张医生',
      title: '主任医师',
      department: '内科',
      expertise: ['心血管疾病', '高血压'],
      rating: 4.8,
    ),
    DoctorInfo(
      id: '2',
      name: '李医生',
      title: '副主任医师',
      department: '神经内科',
      expertise: ['头痛', '癫痫'],
      rating: 4.6,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '选择医生',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Text(
          '您可以选择希望进行会诊的医生，也可以由AI助手为您智能匹配',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 16),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _doctors.length,
          separatorBuilder: (context, index) => const Divider(),
          itemBuilder: (context, index) {
            final doctor = _doctors[index];
            final isSelected = widget.selectedDoctors.contains(doctor.id);

            return CheckboxListTile(
              value: isSelected,
              onChanged: (selected) {
                final newSelection = List<String>.from(widget.selectedDoctors);
                if (selected == true) {
                  newSelection.add(doctor.id);
                } else {
                  newSelection.remove(doctor.id);
                }
                widget.onChanged(newSelection);
              },
              title: Row(
                children: [
                  Text(doctor.name),
                  const SizedBox(width: 8),
                  Text(
                    doctor.title,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(doctor.department),
                  const SizedBox(height: 4),
                  Wrap(
                    spacing: 4,
                    children: doctor.expertise.map((e) {
                      return Chip(
                        label: Text(
                          e,
                          style: const TextStyle(fontSize: 12),
                        ),
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      );
                    }).toList(),
                  ),
                ],
              ),
              secondary: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.star,
                        size: 16,
                        color: Colors.amber,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        doctor.rating.toString(),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                  if (!doctor.isAvailable)
                    Text(
                      '暂不可约',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.red,
                      ),
                    ),
                ],
              ),
              enabled: doctor.isAvailable,
            );
          },
        ),
        const SizedBox(height: 16),
        OutlinedButton(
          onPressed: () {
            widget.onChanged([]);
          },
          child: const Text('由AI助手智能匹配'),
        ),
      ],
    );
  }
} 