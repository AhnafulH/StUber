import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class MapPage extends StatefulWidget {
  const MapPage({Key? key}) : super(key: key);

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  GoogleMapController? _controller;
  final CameraPosition _initialCameraPosition = const CameraPosition(
    target: LatLng(53.524297, -113.535773), // San Francisco coordinates
    zoom: 14.0,
  );

  final Set<Marker> _markers = {};

  @override
  void initState() {
    super.initState();
    // Initialize markers if needed
    _markers.add(
      const Marker(
        markerId: MarkerId('default_marker'),
        position: LatLng(53.524297, -113.535773),
        infoWindow: InfoWindow(title: 'San Francisco', snippet: 'The Golden Gate City'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Google Maps Demo'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: GoogleMap(
        mapType: MapType.normal,
        initialCameraPosition: _initialCameraPosition,
        markers: _markers,
        onMapCreated: (GoogleMapController controller) {
          _controller = controller;
        },
      ),
      // floatingActionButton: FloatingActionButton(
      //   onPressed: () {
      //     // Add functionality like adding a marker or changing the view
      //     _addMarker();
      //   },
      //   child: const Icon(Icons.add_location),
      // ),
    );
  }

  // void _addMarker() {
  //   setState(() {
  //     _markers.add(
  //       Marker(
  //         markerId: MarkerId('marker_${_markers.length}'),
  //         position: LatLng(
  //           _initialCameraPosition.target.latitude + (0.001 * _markers.length),
  //           _initialCameraPosition.target.longitude,
  //         ),
  //         infoWindow: InfoWindow(
  //           title: 'New Location ${_markers.length}',
  //           snippet: 'Added location',
  //         ),
  //       ),
  //     );
  //   });
  // }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
}