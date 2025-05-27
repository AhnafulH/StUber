import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';



class MapController {
  _MapComponentState? _state;
  
  void _setState(_MapComponentState state) {
    _state = state;
  }
  
  void addMarker(LatLng position, {String? title, String? snippet}) {
    _state?.addMarker(position, title: title, snippet: snippet);
  }
  
  void removeMarker(String markerId) {
    _state?.removeMarker(markerId);
  }
  
  void clearMarkers() {
    _state?.clearMarkers();
  }
  
  void moveCamera(LatLng position, {double zoom = 14.0}) {
    _state?.moveCamera(position, zoom: zoom);
  }
  
  void animateCamera(LatLng position, {double zoom = 14.0}) {
    _state?.animateCamera(position, zoom: zoom);
  }
  
  Set<Marker> get markers => _state?._markers ?? {};
  
  GoogleMapController? get mapController => _state?._controller;
}



class MapComponent extends StatefulWidget {
  final MapController? controller;
  final CameraPosition? initialCameraPosition;
  final MapType mapType;
  final Set<Marker>? initialMarkers;
  final void Function(GoogleMapController)? onMapCreated;
  
  const MapComponent({
    Key? key,
    this.controller,
    this.initialCameraPosition,
    this.mapType = MapType.normal,
    this.initialMarkers,
    this.onMapCreated,
  }) : super(key: key);

  @override
  State<MapComponent> createState() => _MapComponentState();
}

class _MapComponentState extends State<MapComponent> {
  GoogleMapController? _controller;
  late CameraPosition _initialCameraPosition;
  final Set<Marker> _markers = {};

  @override
  void initState() {
    super.initState();
    
    // Register this state with the controller
    widget.controller?._setState(this);
    
    // Set initial camera position
    _initialCameraPosition = widget.initialCameraPosition ?? 
        const CameraPosition(
          target: LatLng(53.524297, -113.535773),
          zoom: 14.0,
        );
    
    // Add initial markers
    if (widget.initialMarkers != null) {
      _markers.addAll(widget.initialMarkers!);
    } else {
      // Add default marker
      _markers.add(
        const Marker(
          markerId: MarkerId('default_marker'),
          position: LatLng(53.524297, -113.535773),
          infoWindow: InfoWindow(title: 'Edmonton', snippet: 'The UofA'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return GoogleMap(
      mapType: widget.mapType,
      initialCameraPosition: _initialCameraPosition,
      markers: _markers,
      onMapCreated: (GoogleMapController controller) {
        _controller = controller;
        widget.onMapCreated?.call(controller);
      },
      // markers: {
      //   Marker(
      //     markerId: MarkerId("_currentloaction"),
      //     icon: BitmapDescriptor.defaultMarker,
      //     position: LatLng(53.524297, -113.535773),
      //   )
      // },
    );
  }

  // Methods that can be called through the controller
  void addMarker(LatLng position, {String? title, String? snippet}) {
    final String markerId = 'marker_${DateTime.now().millisecondsSinceEpoch}';
    setState(() {
      _markers.add(
        Marker(
          markerId: MarkerId(markerId),
          position: position,
          infoWindow: InfoWindow(
            title: title ?? 'Marker',
            snippet: snippet,
          ),
        ),
      );
    });
  }

  void removeMarker(String markerId) {
    setState(() {
      _markers.removeWhere((marker) => marker.markerId.value == markerId);
    });
  }

  void clearMarkers() {
    setState(() {
      _markers.clear();
    });
  }

  void moveCamera(LatLng position, {double zoom = 14.0}) {
    _controller?.moveCamera(
      CameraUpdate.newCameraPosition(
        CameraPosition(target: position, zoom: zoom),
      ),
    );
  }

  void animateCamera(LatLng position, {double zoom = 14.0}) {
    _controller?.animateCamera(
      CameraUpdate.newCameraPosition(
        CameraPosition(target: position, zoom: zoom),
      ),
    );
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
}