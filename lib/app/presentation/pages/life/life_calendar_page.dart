class LifeCalendarPage extends GetView<LifeCalendarController> {
  const LifeCalendarPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('生活日历'),
        actions: [
          IconButton(
            icon: const Icon(Icons.today),
            onPressed: controller.goToToday,
          ),
        ],
      ),
      body: Column(
        children: [
          // 日历视图
          TableCalendar(
            firstDay: DateTime.utc(2020, 1, 1),
            lastDay: DateTime.utc(2030, 12, 31),
            focusedDay: controller.focusedDay.value,
            selectedDayPredicate: (day) => isSameDay(controller.selectedDay.value, day),
            onDaySelected: controller.onDaySelected,
            eventLoader: controller.getEventsForDay,
          ),
          
          // 事件列表
          Expanded(
            child: Obx(() => ListView.builder(
              itemCount: controller.selectedEvents.length,
              itemBuilder: (context, index) {
                final event = controller.selectedEvents[index];
                return ListTile(
                  title: Text(event.title),
                  subtitle: Text(event.content),
                  onTap: () => controller.onEventTap(event),
                );
              },
            )),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: controller.addEvent,
        child: const Icon(Icons.add),
      ),
    );
  }
} 