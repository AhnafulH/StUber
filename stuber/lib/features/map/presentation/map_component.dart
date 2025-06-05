import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'dart:math' as math;

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
  
  // Add fitBounds method
  void fitBounds(LatLngBounds bounds) {
    _state?.fitBounds(bounds);
  }
  
  Set<Marker> get markers => _state?._allMarkers ?? {};
  
  GoogleMapController? get mapController => _state?._controller;
}

class MapComponent extends StatefulWidget {
  final MapController? controller;
  final CameraPosition? initialCameraPosition;
  final MapType mapType;
  final Set<Marker>? initialMarkers;
  final Set<Marker> markers; // External markers from parent
  final void Function(GoogleMapController)? onMapCreated;
  
  const MapComponent({
    Key? key,
    this.controller,
    this.initialCameraPosition,
    this.mapType = MapType.normal,
    this.initialMarkers,
    this.markers = const {},
    this.onMapCreated,
  }) : super(key: key);

  @override
  State<MapComponent> createState() => _MapComponentState();
}

class _MapComponentState extends State<MapComponent> {
  GoogleMapController? _controller;
  late CameraPosition _initialCameraPosition;
  final Set<Marker> _internalMarkers = {}; // For markers added via controller

  @override
  void initState() {
    super.initState();
    
    // Register this state with the controller
    widget.controller?._setState(this);
    
    // Set initial camera position
    _initialCameraPosition = widget.initialCameraPosition ?? 
        const CameraPosition(
          target: LatLng(53.524297, -113.535773),
          zoom: 11.0, // Zoom out a bit to show Edmonton area
        );
    
    // Only add initial markers if explicitly provided - NO DEFAULT MARKERS
    if (widget.initialMarkers != null) {
      _internalMarkers.addAll(widget.initialMarkers!);
    }
    // Removed the default hardcoded marker
  }

  // Combine external markers (from parent) with internal markers
  Set<Marker> get _allMarkers {
    Set<Marker> allMarkers = {};
    allMarkers.addAll(widget.markers); // External markers from parent
    allMarkers.addAll(_internalMarkers); // Internal markers from controller
    return allMarkers;
  }

  @override
  Widget build(BuildContext context) {
    return GoogleMap(
      mapType: widget.mapType,
      initialCameraPosition: _initialCameraPosition,
      markers: _allMarkers, // Use combined markers
      onMapCreated: (GoogleMapController controller) {
        _controller = controller;
        widget.onMapCreated?.call(controller);
        
        // If we have external markers, fit them in view
        if (widget.markers.isNotEmpty) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            _fitMarkersInView();
          });
        }
      },
      myLocationEnabled: true,
      myLocationButtonEnabled: true,
      zoomControlsEnabled: true,
      compassEnabled: true,
    );
  }

  // Fit all markers in view (only if there are markers to fit)
  void _fitMarkersInView() {
    if (_allMarkers.isEmpty || _controller == null) return;
    
    // If only one marker, just center on it
    if (_allMarkers.length == 1) {
      final marker = _allMarkers.first;
      animateCamera(marker.position, zoom: 15.0);
      return;
    }

    // If multiple markers, fit them all in view
    double minLat = double.infinity;
    double maxLat = -double.infinity;
    double minLng = double.infinity;
    double maxLng = -double.infinity;

    for (Marker marker in _allMarkers) {
      minLat = math.min(minLat, marker.position.latitude);
      maxLat = math.max(maxLat, marker.position.latitude);
      minLng = math.min(minLng, marker.position.longitude);
      maxLng = math.max(maxLng, marker.position.longitude);
    }

    // Add padding
    double latPadding = (maxLat - minLat) * 0.3;
    double lngPadding = (maxLng - minLng) * 0.3;

    // Minimum padding
    latPadding = math.max(latPadding, 0.01);
    lngPadding = math.max(lngPadding, 0.01);

    LatLngBounds bounds = LatLngBounds(
      southwest: LatLng(minLat - latPadding, minLng - lngPadding),
      northeast: LatLng(maxLat + latPadding, maxLng + lngPadding),
    );

    _controller!.animateCamera(
      CameraUpdate.newLatLngBounds(bounds, 100.0),
    );
  }

  // Methods that can be called through the controller
  void addMarker(LatLng position, {String? title, String? snippet}) {
    final String markerId = 'marker_${DateTime.now().millisecondsSinceEpoch}';
    setState(() {
      _internalMarkers.add(
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
      _internalMarkers.removeWhere((marker) => marker.markerId.value == markerId);
    });
  }

  void clearMarkers() {
    setState(() {
      _internalMarkers.clear();
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

  void fitBounds(LatLngBounds bounds) {
    _controller?.animateCamera(
      CameraUpdate.newLatLngBounds(bounds, 100.0),
    );
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
}