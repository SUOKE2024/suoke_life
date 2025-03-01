import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:intl/intl.dart';

import '../../../domain/entities/appointment.dart';
import '../../providers/appointment_providers.dart';
import '../../providers/auth_providers.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/form/form_field_wrapper.dart';

@RoutePage()
class AppointmentCreateScreen extends ConsumerStatefulWidget {
  final String? serviceId;
  final String? providerId;

  const AppointmentCreateScreen({
    Key? key,
    @QueryParam('serviceId') this.serviceId,
    @QueryParam('providerId') this.providerId,
  }) : super(key: key);

  @override
  ConsumerState<AppointmentCreateScreen> createState() => _AppointmentCreateScreenState();
}

class _AppointmentCreateScreenState extends ConsumerState<AppointmentCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  
  // 表单控制器
  late TextEditingController _notesController;
  
  // 表单数据
  String _selectedServiceId = '';
  String _selectedProviderId = '';
  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  DateTime? _selectedStartTime;
  DateTime? _selectedEndTime;
  
  // 页面状态
  bool _isLoading = false;
  String? _errorMessage;
  List<DateTime> _availableTimeSlots = [];
  
  // 模拟数据
  final List<Map<String, dynamic>> _services = [
    {'id': 'srv_1', 'name': '中医诊断', 'duration': 60, 'price': 200.0},
    {'id': 'srv_2', 'name': '健康咨询', 'duration': 30, 'price': 100.0},
    {'id': 'srv_3', 'name': '营养指导', 'duration': 45, 'price': 150.0},
    {'id': 'srv_4', 'name': '运动指导', 'duration': 60, 'price': 180.0},
    {'id': 'srv_5', 'name': '心理咨询', 'duration': 90, 'price': 300.0},
  ];
  
  final List<Map<String, dynamic>> _providers = [
    {'id': 'prv_1', 'name': '张医生', 'specialty': '中医内科'},
    {'id': 'prv_2', 'name': '李医生', 'specialty': '营养学'},
    {'id': 'prv_3', 'name': '王医生', 'specialty': '运动医学'},
    {'id': 'prv_4', 'name': '赵医生', 'specialty': '心理健康'},
    {'id': 'prv_5', 'name': '钱医生', 'specialty': '中医外科'},
  ];

  @override
  void initState() {
    super.initState();
    _notesController = TextEditingController();
    
    // 如果有预设的服务和提供者ID，则设置选中状态
    if (widget.serviceId != null && widget.serviceId!.isNotEmpty) {
      _selectedServiceId = widget.serviceId!;
    } else if (_services.isNotEmpty) {
      _selectedServiceId = _services.first['id'];
    }
    
    if (widget.providerId != null && widget.providerId!.isNotEmpty) {
      _selectedProviderId = widget.providerId!;
    } else if (_providers.isNotEmpty) {
      _selectedProviderId = _providers.first['id'];
    }
    
    // 加载可用时间段
    _loadAvailableTimeSlots();
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _loadAvailableTimeSlots() async {
    if (_selectedServiceId.isEmpty || _selectedProviderId.isEmpty) {
      return;
    }
    
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _selectedStartTime = null;
      _selectedEndTime = null;
    });
    
    try {
      await ref.read(appointmentProvider.notifier).getAvailableTimeSlots(
        serviceId: _selectedServiceId,
        providerId: _selectedProviderId,
        date: _selectedDate,
      );
      
      final slots = ref.read(appointmentProvider).availableTimeSlots;
      
      setState(() {
        _availableTimeSlots = slots;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '加载可用时间段失败: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _createAppointment() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    
    if (_selectedStartTime == null || _selectedEndTime == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请选择预约时间')),
      );
      return;
    }
    
    final authState = ref.read(authStateProvider);
    if (authState.currentUser == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请先登录')),
      );
      return;
    }
    
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    
    try {
      final appointment = await ref.read(appointmentProvider.notifier).createAppointment(
        userId: authState.currentUser!.id,
        serviceId: _selectedServiceId,
        providerId: _selectedProviderId,
        appointmentDate: DateTime(_selectedDate.year, _selectedDate.month, _selectedDate.day),
        startTime: _selectedStartTime!,
        endTime: _selectedEndTime!,
        notes: _notesController.text.isNotEmpty ? _notesController.text : null,
      );
      
      setState(() {
        _isLoading = false;
      });
      
      if (appointment != null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('预约创建成功')),
          );
          // 导航回上一页或预约列表页
          context.router.pop();
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('预约创建失败')),
          );
        }
      }
    } catch (e) {
      setState(() {
        _errorMessage = '创建预约失败: $e';
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('创建预约失败: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('创建预约'),
      ),
      body: LoadingOverlay(
        isLoading: _isLoading,
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 服务选择
                FormFieldWrapper(
                  label: '服务项目',
                  child: DropdownButtonFormField<String>(
                    value: _selectedServiceId.isNotEmpty ? _selectedServiceId : null,
                    decoration: const InputDecoration(
                      hintText: '请选择服务项目',
                      border: OutlineInputBorder(),
                    ),
                    items: _services.map((service) {
                      return DropdownMenuItem<String>(
                        value: service['id'],
                        child: Text('${service['name']} (¥${service['price'].toStringAsFixed(2)})'),
                      );
                    }).toList(),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请选择服务项目';
                      }
                      return null;
                    },
                    onChanged: (value) {
                      if (value != null && value != _selectedServiceId) {
                        setState(() {
                          _selectedServiceId = value;
                          _selectedStartTime = null;
                          _selectedEndTime = null;
                        });
                        _loadAvailableTimeSlots();
                      }
                    },
                  ),
                ),
                const SizedBox(height: 16),
                
                // 服务提供者选择
                FormFieldWrapper(
                  label: '服务提供者',
                  child: DropdownButtonFormField<String>(
                    value: _selectedProviderId.isNotEmpty ? _selectedProviderId : null,
                    decoration: const InputDecoration(
                      hintText: '请选择服务提供者',
                      border: OutlineInputBorder(),
                    ),
                    items: _providers.map((provider) {
                      return DropdownMenuItem<String>(
                        value: provider['id'],
                        child: Text('${provider['name']} (${provider['specialty']})'),
                      );
                    }).toList(),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请选择服务提供者';
                      }
                      return null;
                    },
                    onChanged: (value) {
                      if (value != null && value != _selectedProviderId) {
                        setState(() {
                          _selectedProviderId = value;
                          _selectedStartTime = null;
                          _selectedEndTime = null;
                        });
                        _loadAvailableTimeSlots();
                      }
                    },
                  ),
                ),
                const SizedBox(height: 16),
                
                // 日期选择
                FormFieldWrapper(
                  label: '预约日期',
                  child: InkWell(
                    onTap: () async {
                      final now = DateTime.now();
                      final firstDate = now;
                      final lastDate = now.add(const Duration(days: 90));
                      
                      final pickedDate = await showDatePicker(
                        context: context,
                        initialDate: _selectedDate,
                        firstDate: firstDate,
                        lastDate: lastDate,
                      );
                      
                      if (pickedDate != null && pickedDate != _selectedDate) {
                        setState(() {
                          _selectedDate = pickedDate;
                          _selectedStartTime = null;
                          _selectedEndTime = null;
                        });
                        _loadAvailableTimeSlots();
                      }
                    },
                    child: InputDecorator(
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        suffixIcon: Icon(Icons.calendar_today),
                      ),
                      child: Text(
                        DateFormat('yyyy年MM月dd日').format(_selectedDate),
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                
                // 时间段选择
                FormFieldWrapper(
                  label: '可用时间段',
                  description: '请选择预约的开始时间',
                  child: _availableTimeSlots.isEmpty
                      ? const Center(
                          child: Padding(
                            padding: EdgeInsets.all(16),
                            child: Text('当前日期没有可用的时间段'),
                          ),
                        )
                      : Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: _availableTimeSlots.map((timeSlot) {
                            final isSelected = _selectedStartTime == timeSlot;
                            
                            // 检查是否有足够的连续时间段
                            final selectedService = _services.firstWhere(
                              (service) => service['id'] == _selectedServiceId,
                              orElse: () => {'duration': 30},
                            );
                            final durationInMinutes = selectedService['duration'] as int;
                            
                            // 检查是否可以选择这个时间段
                            bool canSelect = true;
                            final endTime = timeSlot.add(Duration(minutes: durationInMinutes));
                            
                            // 简化处理，实际应用中应该检查这个时间段是否可用
                            
                            return ChoiceChip(
                              label: Text(DateFormat('HH:mm').format(timeSlot)),
                              selected: isSelected,
                              onSelected: canSelect
                                  ? (selected) {
                                      if (selected) {
                                        setState(() {
                                          _selectedStartTime = timeSlot;
                                          _selectedEndTime = endTime;
                                        });
                                      } else {
                                        setState(() {
                                          _selectedStartTime = null;
                                          _selectedEndTime = null;
                                        });
                                      }
                                    }
                                  : null,
                              backgroundColor: canSelect ? null : Colors.grey[300],
                            );
                          }).toList(),
                        ),
                ),
                if (_selectedStartTime != null && _selectedEndTime != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    '预约时间: ${DateFormat('HH:mm').format(_selectedStartTime!)} - ${DateFormat('HH:mm').format(_selectedEndTime!)}',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.blue,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ],
                const SizedBox(height: 16),
                
                // 备注
                FormFieldWrapper(
                  label: '备注',
                  description: '可选，添加关于预约的特殊要求或说明',
                  child: TextFormField(
                    controller: _notesController,
                    decoration: const InputDecoration(
                      hintText: '请输入备注信息（可选）',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 3,
                  ),
                ),
                const SizedBox(height: 24),
                
                // 错误信息
                if (_errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.red[50],
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: Colors.red),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error, color: Colors.red),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(color: Colors.red),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                
                // 提交按钮
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _createAppointment,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text('创建预约'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
} 