/// Base view class that provides common functionality for all views.
/// 
/// Features:
/// - Controller binding
/// - Loading state handling
/// - Error handling
/// - Lifecycle management
abstract class BaseView<T extends BaseController> extends GetView<T> {
  const BaseView({super.key});

  /// Build method with loading and error handling
  @override
  Widget build(BuildContext context) {
    return Obx(() {
      // Show loading indicator
      if (controller.isLoading) {
        return buildLoading();
      }

      // Show error message
      if (controller.error != null) {
        return buildError(controller.error!);
      }

      // Build main content
      return buildContent(context);
    });
  }

  /// Build main content
  Widget buildContent(BuildContext context);

  /// Build loading indicator
  Widget buildLoading() {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }

  /// Build error widget
  Widget buildError(String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            color: Colors.red,
            size: 48,
          ),
          const SizedBox(height: 16),
          Text(
            message,
            style: const TextStyle(color: Colors.red),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => controller.clearError(),
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  /// Show snackbar message
  void showMessage(
    String message, {
    String? title,
    Duration duration = const Duration(seconds: 3),
    SnackPosition position = SnackPosition.BOTTOM,
  }) {
    Get.snackbar(
      title ?? 'Message',
      message,
      duration: duration,
      snackPosition: position,
    );
  }

  /// Show error snackbar
  void showError(
    String message, {
    String? title,
    Duration duration = const Duration(seconds: 3),
    SnackPosition position = SnackPosition.BOTTOM,
  }) {
    Get.snackbar(
      title ?? 'Error',
      message,
      duration: duration,
      snackPosition: position,
      backgroundColor: Colors.red,
      colorText: Colors.white,
    );
  }

  /// Show success snackbar
  void showSuccess(
    String message, {
    String? title,
    Duration duration = const Duration(seconds: 3),
    SnackPosition position = SnackPosition.BOTTOM,
  }) {
    Get.snackbar(
      title ?? 'Success',
      message,
      duration: duration,
      snackPosition: position,
      backgroundColor: Colors.green,
      colorText: Colors.white,
    );
  }
} 