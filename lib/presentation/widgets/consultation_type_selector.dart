import 'package:flutter/material.dart';
import '../../services/consultation_service.dart';

class ConsultationTypeSelector extends StatelessWidget {
  final ConsultationType value;
  final ValueChanged<ConsultationType> onChanged;

  const ConsultationTypeSelector({
    Key? key,
    required this.value,
    required this.onChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '会诊类型',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: ConsultationType.values.map((type) {
            final isSelected = type == value;
            final isUrgent = type == ConsultationType.emergencyConsultation;

            return ChoiceChip(
              label: Text(_getTypeLabel(type)),
              selected: isSelected,
              onSelected: (selected) {
                if (selected) {
                  onChanged(type);
                }
              },
              selectedColor: isUrgent ? Colors.red : Theme.of(context).primaryColor,
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : null,
                fontWeight: isSelected ? FontWeight.bold : null,
              ),
              avatar: isUrgent
                  ? const Icon(Icons.emergency, size: 18, color: Colors.white)
                  : null,
            );
          }).toList(),
        ),
        const SizedBox(height: 8),
        Text(
          _getTypeDescription(value),
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  String _getTypeLabel(ConsultationType type) {
    switch (type) {
      case ConsultationType.generalConsultation:
        return '一般会诊';
      case ConsultationType.emergencyConsultation:
        return '急诊会诊';
      case ConsultationType.followUpConsultation:
        return '复诊会诊';
      case ConsultationType.specialistConsultation:
        return '专家会诊';
    }
  }

  String _getTypeDescription(ConsultationType type) {
    switch (type) {
      case ConsultationType.generalConsultation:
        return '适用于常规病情咨询和诊断';
      case ConsultationType.emergencyConsultation:
        return '适用于紧急情况，将优先安排专家进行诊断';
      case ConsultationType.followUpConsultation:
        return '适用于复查和后续治疗跟进';
      case ConsultationType.specialistConsultation:
        return '适用于疑难杂症，将安排多位专家进行会诊';
    }
  }
} 