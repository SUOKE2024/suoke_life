import 'package:flutter/material.dart';

import '../../services/consultation_service.dart';
import '../widgets/consultation_type_selector.dart';
import '../widgets/symptom_input.dart';
import '../widgets/datetime_picker.dart';

class ConsultationRequestPage extends StatefulWidget {
  const ConsultationRequestPage({Key? key}) : super(key: key);

  @override
  State<ConsultationRequestPage> createState() => _ConsultationRequestPageState();
}

class _ConsultationRequestPageState extends State<ConsultationRequestPage> {
  final _formKey = GlobalKey<FormState>();
  ConsultationType _type = ConsultationType.generalConsultation;
  String _symptoms = '';
  DateTime _dateTime = DateTime.now().add(const Duration(days: 1));
  bool _isSubmitting = false;
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('预约会诊'),
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ConsultationTypeSelector(
                value: _type,
                onChanged: (type) => setState(() => _type = type),
              ),
              const SizedBox(height: 24),
              SymptomInput(
                initialValue: _symptoms,
                onChanged: (value) => _symptoms = value,
              ),
              const SizedBox(height: 24),
              CustomDateTimePicker(
                initialDateTime: _dateTime,
                onChanged: (dateTime) => setState(() => _dateTime = dateTime),
                minDateTime: DateTime.now().add(const Duration(hours: 1)),
                maxDateTime: DateTime.now().add(const Duration(days: 30)),
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _isSubmitting ? null : _submitRequest,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isSubmitting 
                  ? const CircularProgressIndicator()
                  : const Text('提交会诊申请'),
              ),
              const SizedBox(height: 16),
              Text(
                '提交后,AI助手将根据您的症状描述和时间安排,为您匹配最合适的专家。',
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _submitRequest() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final request = ConsultationRequest(
        patientId: 'current_user_id', // TODO: 从用户服务获取
        type: _type,
        symptoms: _symptoms,
        scheduledTime: _dateTime,
      );

      await context.read<ConsultationService>().submitRequest(request);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('会诊申请已提交,AI助手正在为您安排专家')),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('提交失败: ${e.toString()}')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }
} 