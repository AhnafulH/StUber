import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:animated_toggle_switch/animated_toggle_switch.dart';

class MapPage extends StatefulWidget {
  const MapPage({Key? key}) : super(key: key);

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  GoogleMapController? _controller;
  final CameraPosition _initialCameraPosition = const CameraPosition(
    target: LatLng(53.524297, -113.535773),
    zoom: 14.0,
  );
  bool _isRequestingRide = true;
  final Set<Marker> _markers = {};

  @override
  void initState() {
    super.initState();
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
      body: Stack(
        children: [
          // Google Map
          GoogleMap(
            mapType: MapType.normal,
            initialCameraPosition: _initialCameraPosition,
            markers: _markers,
            onMapCreated: (GoogleMapController controller) {
              _controller = controller;
            },
          ),

          // Toggle switch on top with improved styling
          Positioned(
            top: 100,
            left: 50,
            right: 50,
            child: Center(
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(35),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.25),
                      blurRadius: 15,
                      offset: const Offset(0, 5),
                      spreadRadius: 2,
                    )
                  ],
                ),
                child: AnimatedToggleSwitch<bool>.size(
                  current: _isRequestingRide,
                  values: const [true, false],
                  iconOpacity: 1.0,
                  indicatorSize: const Size.fromWidth(double.infinity),
                  customIconBuilder: (context, local, global) {
                    // Custom widget for each toggle option with improved styling
                    return Container(
                      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          // Improved icon styling
                          AnimatedSwitcher(
                            duration: const Duration(milliseconds: 300),
                            child: Icon(
                              local.value ? Icons.people_alt_rounded : Icons.directions_car_filled_rounded,
                              key: ValueKey<bool>(local.value),
                              color: Color.lerp(
                                Colors.grey[700],
                                Colors.white,
                                local.animationValue
                              ),
                              size: 20,
                            ),
                          ),
                          const SizedBox(width: 10),
                          // Text label with nicer typography
                          Text(
                            local.value ? 'Request' : 'Offer',
                            style: TextStyle(
                              color: Color.lerp(
                                Colors.grey[800],
                                Colors.white,
                                local.animationValue
                              ),
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                              letterSpacing: 0.3,
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                  borderWidth: 0,
                  height: 42,
                  iconAnimationType: AnimationType.onHover,
                  style: ToggleStyle(
                    indicatorColor: const Color(0xFF1E88E5), // Material blue
                    backgroundColor: Colors.white,
                    borderColor: Colors.transparent,
                    borderRadius: BorderRadius.circular(35),
                  ),
                  // Shadow effect is applied via the outer container instead
                  selectedIconScale: 1.0,
                  animationDuration: const Duration(milliseconds: 400),
                  onChanged: (value) => setState(() => _isRequestingRide = value),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
}