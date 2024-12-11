import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class MapView extends StatefulWidget {
  final double latitude;
  final double longitude;
  final List<Map<String, dynamic>> markers;
  
  const MapView({
    Key? key,
    required this.latitude,
    required this.longitude,
    this.markers = const [],
  }) : super(key: key);

  @override
  State<MapView> createState() => _MapViewState();
}

class _MapViewState extends State<MapView> {
  late final WebViewController controller;

  @override
  void initState() {
    super.initState();
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..loadHtmlString(_generateHtml());
  }

  String _generateHtml() {
    final mapKey = dotenv.env['TENCENT_MAP_KEY'];
    final markersJson = jsonEncode(widget.markers);
    return '''
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>腾讯地图</title>
        <script src="https://map.qq.com/api/gljs?v=1.exp&key=$mapKey&referer=suoke_life"></script>
        <style>
          html,body,#map { height: 100%; margin: 0; padding: 0; }
          #map { touch-action: none; }
        </style>
      </head>
      <body>
        <div id="map"></div>
        <script>
          var map = new TMap.Map('map', {
            center: new TMap.LatLng(${widget.latitude}, ${widget.longitude}),
            zoom: 15
          });
          
          var markers = $markersJson;
          markers.forEach(function(marker) {
            new TMap.Marker({
              map: map,
              position: new TMap.LatLng(marker.latitude, marker.longitude),
              title: marker.title
            });
          });
        </script>
      </body>
      </html>
    ''';
  }

  @override
  Widget build(BuildContext context) {
    return WebViewWidget(controller: controller);
  }
} 