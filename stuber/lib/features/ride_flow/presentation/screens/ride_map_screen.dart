import 'package:flutter/material.dart';
import 'package:stuber/pages/map_page.dart';
import 'package:stuber/features/ride_request/presentation/widget/bottom_sheet.dart';

class RideMapScreen extends StatefulWidget {
  const RideMapScreen({super.key});

  @override
  State<RideMapScreen> createState() => _RideMapScreenState();
}

class _RideMapScreenState extends State<RideMapScreen> {
  final DraggableScrollableController _bottomSheetController = DraggableScrollableController();
  bool _isRequestingRide = true; // Track the current mode

  // Handle mode changes (request or offer)
  void onModeChanged(bool isRequestingRide) {
    setState(() {
      _isRequestingRide = isRequestingRide;
    });
    
    // You can add additional logic here based on the selected mode
    // For example, update map markers, show different pickup points, etc.
    print('Mode changed to: ${isRequestingRide ? "Request Ride" : "Offer Ride"}');
  }

  // Handle confirm button press
  void onConfirm() {
    // Add your logic for handling ride request or offer confirmation
    if (_isRequestingRide) {
      // Handle ride request
      print('Ride requested!');
      // You might navigate to a confirmation screen or show a loading indicator
    } else {
      // Handle ride offer
      print('Ride offered!');
      // You might navigate to a driver matching screen or show details entry
    }
    
    // Optional: collapse the bottom sheet after confirmation
    _bottomSheetController.animateTo(
      0.1, // Collapse to minimum size
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  @override
  void dispose() {
    _bottomSheetController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Fullscreen map
          const MapPage(),
          
          // Draggable bottom sheet
          DraggableScrollableSheet(
            initialChildSize: 0.3,
            minChildSize: 0.1,
            maxChildSize: 0.6,
            controller: _bottomSheetController,
            builder: (context, scrollController) {
              return RideBottomSheet(
                onModeChanged: onModeChanged, 
                onConfirm: onConfirm,
              );
            },
          ),
        ],
      ),
    );
  }
}
