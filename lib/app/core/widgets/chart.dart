import 'package:flutter/material.dart';

/// 图表组件
class AppChart extends StatelessWidget {
  final List<ChartData> data;
  final String? title;
  final double? height;
  final Color? lineColor;
  final Color? fillColor;
  final bool showDots;
  final bool showLabels;
  final bool showGrid;
  
  const AppChart({
    super.key,
    required this.data,
    this.title,
    this.height = 200,
    this.lineColor,
    this.fillColor,
    this.showDots = true,
    this.showLabels = true,
    this.showGrid = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultLineColor = lineColor ?? theme.primaryColor;
    final defaultFillColor = fillColor ?? defaultLineColor.withOpacity(0.1);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (title != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Text(
              title!,
              style: theme.textTheme.titleMedium,
            ),
          ),
        SizedBox(
          height: height,
          child: CustomPaint(
            size: Size.infinite,
            painter: _ChartPainter(
              data: data,
              lineColor: defaultLineColor,
              fillColor: defaultFillColor,
              showDots: showDots,
              showLabels: showLabels,
              showGrid: showGrid,
            ),
          ),
        ),
      ],
    );
  }
}

class ChartData {
  final double x;
  final double y;
  final String? label;
  
  const ChartData({
    required this.x,
    required this.y,
    this.label,
  });
}

class _ChartPainter extends CustomPainter {
  final List<ChartData> data;
  final Color lineColor;
  final Color fillColor;
  final bool showDots;
  final bool showLabels;
  final bool showGrid;

  _ChartPainter({
    required this.data,
    required this.lineColor,
    required this.fillColor,
    required this.showDots,
    required this.showLabels,
    required this.showGrid,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = lineColor
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final path = Path();
    final points = _getPoints(size);

    // Draw grid
    if (showGrid) {
      _drawGrid(canvas, size);
    }

    // Draw line
    path.moveTo(points[0].dx, points[0].dy);
    for (var i = 1; i < points.length; i++) {
      path.lineTo(points[i].dx, points[i].dy);
    }
    canvas.drawPath(path, paint);

    // Draw fill
    final fillPath = Path.from(path)
      ..lineTo(size.width, size.height)
      ..lineTo(0, size.height)
      ..close();
    canvas.drawPath(
      fillPath,
      Paint()
        ..color = fillColor
        ..style = PaintingStyle.fill,
    );

    // Draw dots
    if (showDots) {
      for (final point in points) {
        canvas.drawCircle(
          point,
          4,
          Paint()
            ..color = lineColor
            ..style = PaintingStyle.fill,
        );
      }
    }

    // Draw labels
    if (showLabels) {
      _drawLabels(canvas, size, points);
    }
  }

  List<Offset> _getPoints(Size size) {
    if (data.isEmpty) return [];

    final xMin = data.map((e) => e.x).reduce(min);
    final xMax = data.map((e) => e.x).reduce(max);
    final yMin = data.map((e) => e.y).reduce(min);
    final yMax = data.map((e) => e.y).reduce(max);

    return data.map((point) {
      final dx = size.width * (point.x - xMin) / (xMax - xMin);
      final dy = size.height * (1 - (point.y - yMin) / (yMax - yMin));
      return Offset(dx, dy);
    }).toList();
  }

  void _drawGrid(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.grey.withOpacity(0.2)
      ..strokeWidth = 1;

    // Draw horizontal lines
    for (var i = 0; i <= 4; i++) {
      final y = size.height * i / 4;
      canvas.drawLine(
        Offset(0, y),
        Offset(size.width, y),
        paint,
      );
    }

    // Draw vertical lines
    for (var i = 0; i <= 4; i++) {
      final x = size.width * i / 4;
      canvas.drawLine(
        Offset(x, 0),
        Offset(x, size.height),
        paint,
      );
    }
  }

  void _drawLabels(Canvas canvas, Size size, List<Offset> points) {
    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );

    for (var i = 0; i < data.length; i++) {
      if (data[i].label != null) {
        textPainter.text = TextSpan(
          text: data[i].label,
          style: const TextStyle(
            color: Colors.grey,
            fontSize: 12,
          ),
        );
        textPainter.layout();
        textPainter.paint(
          canvas,
          Offset(
            points[i].dx - textPainter.width / 2,
            size.height + 4,
          ),
        );
      }
    }
  }

  @override
  bool shouldRepaint(_ChartPainter oldDelegate) {
    return data != oldDelegate.data ||
        lineColor != oldDelegate.lineColor ||
        fillColor != oldDelegate.fillColor ||
        showDots != oldDelegate.showDots ||
        showLabels != oldDelegate.showLabels ||
        showGrid != oldDelegate.showGrid;
  }
} 