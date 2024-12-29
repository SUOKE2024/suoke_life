class LifeRecordDetailPage extends GetView<LifeRecordDetailController> {
  const LifeRecordDetailPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('记录详情'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: controller.editRecord,
          ),
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: controller.deleteRecord,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Obx(() => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              controller.record.value.title,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              controller.record.value.content,
              style: const TextStyle(
                fontSize: 16,
                height: 1.6,
              ),
            ),
            if (controller.record.value.images.isNotEmpty) ...[
              const SizedBox(height: 16),
              GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  mainAxisSpacing: 8,
                  crossAxisSpacing: 8,
                ),
                itemCount: controller.record.value.images.length,
                itemBuilder: (context, index) {
                  return Image.network(
                    controller.record.value.images[index],
                    fit: BoxFit.cover,
                  );
                },
              ),
            ],
          ],
        )),
      ),
    );
  }
} 