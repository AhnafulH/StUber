import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/foundation.dart';
import 'package:stuber/features/map/presentation/map_utils.dart';
import 'dart:async';

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
  
  // Add method to trigger marker fitting
  void fitMarkersInView() {
    _state?.fitMarkersInView();
  }
  
  Set<Marker> get markers => _state?._allMarkers ?? {};
  
  // Access to GoogleMapController as per documentation
  GoogleMapController? get mapController => _state?._googleMapController;
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
  // Global vars as per documentation
  Completer<GoogleMapController> _controller = Completer();
  late GoogleMapController _googleMapController;
  
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
          target: LatLng(53.524297, -113.535773), // Edmonton
          zoom: 10,
        );
    
    // Only add initial markers if explicitly provided
    if (widget.initialMarkers != null) {
      _internalMarkers.addAll(widget.initialMarkers!);
    }
  }

  // Combine external markers (from parent) with internal markers
  Set<Marker> get _allMarkers {
    Set<Marker> allMarkers = {};
    allMarkers.addAll(widget.markers); // External markers from parent
    allMarkers.addAll(_internalMarkers); // Internal markers from controller
    return allMarkers;
  }

  @override
  void didUpdateWidget(MapComponent oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    // Check if markers have changed and auto-fit if they have
    if (widget.markers != oldWidget.markers && widget.markers.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _fitMarkersInView();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return GoogleMap(
      // Add gesture recognizers as per documentation
      gestureRecognizers: Set()
        ..add(Factory<PanGestureRecognizer>(
          () => PanGestureRecognizer())),
      mapType: widget.mapType,
      initialCameraPosition: _initialCameraPosition,
      zoomControlsEnabled: true,
      myLocationEnabled: true,
      myLocationButtonEnabled: true,
      compassEnabled: true,
      onMapCreated: (GoogleMapController controller) {
        _controller.complete(controller);
        _googleMapController = controller;
        _googleMapController.getVisibleRegion();

        // Call parent onMapCreated if provided
        widget.onMapCreated?.call(controller);

        // Auto-fit markers using MapUtils if they exist
        if (_allMarkers.isNotEmpty) {
          _fitMarkersInView();
        }
      },
      // Set markers as per documentation
      markers: Set.from(_allMarkers),
      // compassEnabled: true,
    );
  }

  // Separate method for fitting markers in view
  void _fitMarkersInView() {
    if (_allMarkers.isEmpty) return;
    
    Set<Marker> _markers = Set.from(_allMarkers);
    
    // Use MapUtils exactly as per documentation
    Future.delayed(
      Duration(milliseconds: 200),
      () {
        if (mounted) {
          _googleMapController.animateCamera(
            CameraUpdate.newLatLngBounds(
              MapUtils.boundsFromLatLngList(
                _markers.map((marker) => marker.position).toList()
              ),
              100 // padding
            )
          );
        }
      }
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
    _googleMapController.moveCamera(
      CameraUpdate.newCameraPosition(
        CameraPosition(target: position, zoom: zoom),
      ),
    );
  }

  void animateCamera(LatLng position, {double zoom = 14.0}) {
    if (_controller.isCompleted) {
      _googleMapController.animateCamera(
        CameraUpdate.newCameraPosition(
          CameraPosition(target: position, zoom: zoom),
        ),
      );
    }
  }

  // Add method to manually trigger marker fitting
  void fitMarkersInView() {
    _fitMarkersInView();
  }

  @override
  void dispose() {
    super.dispose();
  }
}