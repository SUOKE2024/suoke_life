import 'package:suoke_life/lib/core/services/payment_service.dart';

class PaymentServiceImpl implements PaymentService {
  @override
  Future<void> processPayment(double amount) async {
    // TODO: Implement payment logic
    print('Payment processed for amount: $amount');
  }
} 