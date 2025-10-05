import 'package:http/http.dart' as http;
import 'dart:convert';

class RouteService {
  static const String _baseUrl = 'https://api.mapbox.com/directions/v5/mapbox';
  static const String _accessToken = 'pk.eyJ1IjoiYWhuYWZ1bCIsImEiOiJjbWI4b24zOTkwazdwMnJvaDhva3c1bmRsIn0.IoyYuI4vuqow-6P-5fQaew';
  
  static Future<RouteData?> getRoute({
    required double startLat,
    required double startLng,
    required double endLat,
    required double endLng,
  }) async {
    
    final coordinates = '$startLng,$startLat;$endLng,$endLat';
    final url = '$_baseUrl/driving/$coordinates?access_token=$_accessToken&geometries=geojson&overview=full&steps=true';
    
    try {
      final response = await http.get(Uri.parse(url));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return RouteData.fromMapboxResponse(data);
      } else {
        print('Route API Error: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('Route Service Error: $e');
      return null;
    }
  }
}

class RouteData {
  final Map<String, dynamic> geometry;
  final double distance; // in meters
  final double duration; // in seconds
  
  RouteData({
    required this.geometry,
    required this.distance,
    required this.duration,
  });
  
  static RouteData? fromMapboxResponse(Map<String, dynamic> response) {
    try {
      final routes = response['routes'] as List;
      if (routes.isEmpty) return null;
      
      final route = routes[0];
      return RouteData(
        geometry: route['geometry'],
        distance: route['distance'].toDouble(),
        duration: route['duration'].toDouble(),
      );
    } catch (e) {
      print('Error parsing route data: $e');
      return null;
    }
  }

  String get formattedDistance {
    if (distance < 1000) {
      return '${distance.round()} m';
    } else {
      return '${(distance / 1000).toStringAsFixed(1)} km';
    }
  }

  String get formattedDuration {
    final minutes = (duration / 60).round();
    if (minutes < 60) {
      return '$minutes min';
    } else {
      final hours = minutes ~/ 60;
      final remainingMinutes = minutes % 60;
      return '${hours}h ${remainingMinutes}m';
    }
  }

  Map<String, dynamic> toApiFormat() {
    return {
      'geometry': geometry,
      'distance': distance,
      'duration': duration,
    };
  }
}