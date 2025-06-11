import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:stuber/features/map/domain/location_service.dart';

class MyLocationWidget extends StatefulWidget {
  @override
  _MyLocationWidgetState createState() => _MyLocationWidgetState();
}

class _MyLocationWidgetState extends State<MyLocationWidget> {
  String _locationMessage = "Press button to get location";
  bool _isLoading = false;

  void _getCurrentLocation() async {
    setState(() {
      _isLoading = true;
      _locationMessage = "Getting location...";
    });

    try {
      Position? position = await LocationService.getCurrentLocation();
      
      if (position != null) {
        setState(() {
          _locationMessage = 'Latitude: ${position.latitude}\n'
                           'Longitude: ${position.longitude}\n'
                           'Accuracy: ${position.accuracy}m';
          _isLoading = false;
        });
      } else {
        setState(() {
          _locationMessage = 'Failed to get location. Check permissions.';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _locationMessage = 'Error: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Location Example'),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _locationMessage,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isLoading ? null : _getCurrentLocation,
              child: _isLoading 
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('Get Current Location'),
            ),
          ],
        ),
      ),
    );
  }
}