// import 'package:flutter/material.dart';
// import 'package:google_maps_flutter/google_maps_flutter.dart';
// import 'package:animated_toggle_switch/animated_toggle_switch.dart';
// import 'package:stuber/features/ride_request/presentation/widget/bottom_sheet.dart';

// class MapPage extends StatefulWidget {
//   const MapPage({Key? key}) : super(key: key);

//   @override
//   State<MapPage> createState() => _MapPageState();
// }

// class _MapPageState extends State<MapPage> {
//   GoogleMapController? _controller;
//   final CameraPosition _initialCameraPosition = const CameraPosition(
//     target: LatLng(53.524297, -113.535773),
//     zoom: 14.0,
//   );
//   bool _isRequestingRide = true;
//   final Set<Marker> _markers = {};
//   final DraggableScrollableController _bottomSheetController = DraggableScrollableController();

//   @override
//   void initState() {
//     super.initState();
//     _markers.add(
//       const Marker(
//         markerId: MarkerId('default_marker'),
//         position: LatLng(53.524297, -113.535773),
//         infoWindow: InfoWindow(title: 'San Francisco', snippet: 'The Golden Gate City'),
//       ),
//     );
//   }

//   void onModeChanged(bool isRequestingRide) {
//     setState(() {
//       _isRequestingRide = isRequestingRide;
//     });
//   }

//   void onConfirm() {
//     // Handle ride request confirmation
//     ScaffoldMessenger.of(context).showSnackBar(
//       const SnackBar(content: Text('Ride requested successfully!')),
//     );
    
//     // You can add more logic here like:
//     // - Showing a progress indicator
//     // - Making an API call to your backend service
//     // - Updating the map with driver information
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       body: Stack(
//         children: [
//           // Google Map
//           GoogleMap(
//             mapType: MapType.normal,
//             initialCameraPosition: _initialCameraPosition,
//             markers: _markers,
//             onMapCreated: (GoogleMapController controller) {
//               _controller = controller;
//             },
//           ),

//           // Toggle switch on top with improved styling
//           Positioned(
//             top: 100,
//             left: 50,
//             right: 50,
//             child: Center(
//               child: Container(
//                 decoration: BoxDecoration(
//                   borderRadius: BorderRadius.circular(35),
//                   boxShadow: [
//                     BoxShadow(
//                       color: Colors.black.withOpacity(0.25),
//                       blurRadius: 15,
//                       offset: const Offset(0, 5),
//                       spreadRadius: 2,
//                     )
//                   ],
//                 ),
//                 child: AnimatedToggleSwitch<bool>.size(
//                   current: _isRequestingRide,
//                   values: const [true, false],
//                   iconOpacity: 1.0,
//                   indicatorSize: const Size.fromWidth(double.infinity),
//                   customIconBuilder: (context, local, global) {
//                     return Container(
//                       padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
//                       child: Row(
//                         mainAxisAlignment: MainAxisAlignment.center,
//                         children: [
//                           AnimatedSwitcher(
//                             duration: const Duration(milliseconds: 300),
//                             child: Icon(
//                               local.value ? Icons.people_alt_rounded : Icons.directions_car_filled_rounded,
//                               key: ValueKey<bool>(local.value),
//                               color: Color.lerp(
//                                 Colors.grey[700],
//                                 Colors.white,
//                                 local.animationValue
//                               ),
//                               size: 20,
//                             ),
//                           ),
//                           const SizedBox(width: 10),
//                           Text(
//                             local.value ? 'Request' : 'Offer',
//                             style: TextStyle(
//                               color: Color.lerp(
//                                 Colors.grey[800],
//                                 Colors.white,
//                                 local.animationValue
//                               ),
//                               fontWeight: FontWeight.w600,
//                               fontSize: 14,
//                               letterSpacing: 0.3,
//                             ),
//                           ),
//                         ],
//                       ),
//                     );
//                   },
//                   borderWidth: 0,
//                   height: 42,
//                   iconAnimationType: AnimationType.onHover,
//                   style: ToggleStyle(
//                     indicatorColor: const Color(0xFF1E88E5),
//                     backgroundColor: Colors.white,
//                     borderColor: Colors.transparent,
//                     borderRadius: BorderRadius.circular(35),
//                   ),
//                   selectedIconScale: 1.0,
//                   animationDuration: const Duration(milliseconds: 400),
//                   onChanged: (value) {
//                     setState(() => _isRequestingRide = value);
//                     onModeChanged(value);
//                   },
//                 ),
//               ),
//             ),
//           ),

//           // Bottom Sheet - Uncommented and properly connected
//           DraggableScrollableSheet(
//             initialChildSize: 0.3,
//             minChildSize: 0.1,
//             maxChildSize: 0.6,
//             controller: _bottomSheetController,
//             builder: (context, scrollController) {
//               return RideBottomSheet(
//                 onModeChanged: onModeChanged, 
//                 onConfirm: onConfirm,
//               );
//             },
//           ),
//         ],
//       ),
//     );
//   }

//   @override
//   void dispose() {
//     _controller?.dispose();
//     _bottomSheetController.dispose();
//     super.dispose();
//   }
// }

import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:animated_toggle_switch/animated_toggle_switch.dart';
import 'package:stuber/features/ride_request/presentation/widget/bottom_sheet.dart';

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
  final DraggableScrollableController _bottomSheetController = DraggableScrollableController();

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

  void onModeChanged(bool isRequestingRide) {
    setState(() {
      _isRequestingRide = isRequestingRide;
    });
    
    // Optional: Expand the bottom sheet slightly to draw attention to the content change
    _bottomSheetController.animateTo(
      0.35, 
      duration: const Duration(milliseconds: 300), 
      curve: Curves.easeInOut
    );
  }

  void onConfirmRequest() {
    // Handle ride request confirmation
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Ride requested successfully!')),
    );
    
    // You can add more logic here for the requesting flow
  }
  
  void onConfirmOffer() {
    // Handle ride offer confirmation
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Ride offer submitted!')),
    );
    
    // You can add more logic here for the offering flow
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
                    return Container(
                      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
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
                    indicatorColor: const Color(0xFF1E88E5),
                    backgroundColor: Colors.white,
                    borderColor: Colors.transparent,
                    borderRadius: BorderRadius.circular(35),
                  ),
                  selectedIconScale: 1.0,
                  animationDuration: const Duration(milliseconds: 400),
                  onChanged: (value) {
                    onModeChanged(value);
                  },
                ),
              ),
            ),
          ),

          // Bottom Sheet that changes based on toggle state
          // DraggableScrollableSheet(
          //   initialChildSize: 0.3,
          //   minChildSize: 0.1,
          //   maxChildSize: 0.6,
          //   controller: _bottomSheetController,
          //   builder: (context, scrollController) {
          //     return RideBottomSheet(
          //       isRequestingRide: _isRequestingRide,
          //       scrollController: scrollController,
          //       onConfirmRequest: onConfirmRequest,
          //       onConfirmOffer: onConfirmOffer,
          //       onModeChanged: onModeChanged,
          //     );
          //   },
          // ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller?.dispose();
    _bottomSheetController.dispose();
    super.dispose();
  }
}