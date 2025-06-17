import 'package:flutter/material.dart';

class RideBottomSheetManager {
  static PersistentBottomSheetController? _controller;

  static void show({
    required BuildContext context,
    required bool isRequestingRide,
    required Function(bool) onModeChanged,
    required Function() onConfirmRequest,
    required Function() onConfirmOffer,
  }) {
    final scaffoldState = Scaffold.of(context);
    
    _controller = scaffoldState.showBottomSheet(
      (context) => RideBottomSheetContent(
        isRequestingRide: isRequestingRide,
        onModeChanged: onModeChanged,
        onConfirmRequest: onConfirmRequest,
        onConfirmOffer: onConfirmOffer,
        onClose: () => _controller?.close(),
      ),
      backgroundColor: Colors.transparent,
      elevation: 0,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      clipBehavior: Clip.antiAliasWithSaveLayer,
    );
  }

  static void hide() {
    _controller?.close();
    _controller = null;
  }
}

// Modified version of your RideBottomSheet to work better with showBottomSheet
class RideBottomSheetContent extends StatefulWidget {
  final Function(bool isRequestingRide) onModeChanged;
  final Function() onConfirmRequest;
  final Function() onConfirmOffer;
  final Function() onClose;
  final bool isRequestingRide;

  const RideBottomSheetContent({
    Key? key,
    required this.onModeChanged,
    required this.onConfirmRequest,
    required this.onConfirmOffer,
    required this.onClose,
    required this.isRequestingRide,
  }) : super(key: key);

  @override
  State<RideBottomSheetContent> createState() => _RideBottomSheetContentState();
}

class _RideBottomSheetContentState extends State<RideBottomSheetContent>
    with TickerProviderStateMixin {
  // Controllers for request ride mode
  final TextEditingController _currentLocationController = 
      TextEditingController(text: "Current Location");
  final TextEditingController _destinationController = TextEditingController();
  
  // Controllers for offer ride mode
  final TextEditingController _startLocationController = TextEditingController();
  final TextEditingController _endLocationController = TextEditingController();
  final TextEditingController _departureTimeController = TextEditingController();
  final TextEditingController _priceController = TextEditingController();
  
  // State variables
  int _passengerCount = 1;
  int _availableSeats = 3;
  
  // Animation controllers
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    );
    _fadeController.forward();
  }

  @override
  void dispose() {
    _currentLocationController.dispose();
    _destinationController.dispose();
    _startLocationController.dispose();
    _endLocationController.dispose();
    _departureTimeController.dispose();
    _priceController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      // No need for decoration here - showBottomSheet handles it
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.8, // Max 80% of screen
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildHeader(),
          Flexible(
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: widget.isRequestingRide 
                  ? _buildRequestRideContent() 
                  : _buildOfferRideContent(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
      child: Column(
        children: [
          // Drag handle - showBottomSheet provides this automatically
          // But we can add our own for visual consistency
          Container(
            width: 50,
            height: 5,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(3),
            ),
          ),
          const SizedBox(height: 16),
          
          // Optional: Add a close button
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                widget.isRequestingRide ? 'Request a Ride' : 'Offer a Ride',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              IconButton(
                onPressed: widget.onClose,
                icon: const Icon(Icons.close),
                style: IconButton.styleFrom(
                  backgroundColor: Colors.grey[100],
                ),
              ),
            ],
          ),
          
          // Toggle buttons (if you want them)
          Container(
            margin: const EdgeInsets.only(top: 16),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(25),
            ),
            padding: const EdgeInsets.all(4),
            child: Row(
              children: [
                Expanded(
                  child: _buildToggleButton(
                    'Request Ride',
                    widget.isRequestingRide,
                    () => widget.onModeChanged(true),
                    Icons.directions_car,
                  ),
                ),
                Expanded(
                  child: _buildToggleButton(
                    'Offer Ride',
                    !widget.isRequestingRide,
                    () => widget.onModeChanged(false),
                    Icons.car_rental,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildToggleButton(
    String text,
    bool isSelected,
    VoidCallback onTap,
    IconData icon,
  ) {
    return GestureDetector(
      onTap: () {
        onTap();
        _fadeController.reset();
        _fadeController.forward();
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? Theme.of(context).primaryColor : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
          boxShadow: isSelected ? [
            BoxShadow(
              color: Theme.of(context).primaryColor.withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ] : null,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.white : Colors.grey[600],
              size: 18,
            ),
            const SizedBox(width: 6),
            Text(
              text,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.grey[600],
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Rest of your existing methods remain the same...
  Widget _buildRequestRideContent() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: Column(
          children: [
            const SizedBox(height: 16),
            // Your existing request ride content...
            Container(
              height: 200,
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(
                child: Text('Request Ride Content Here'),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildOfferRideContent() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: Column(
          children: [
            const SizedBox(height: 16),
            // Your existing offer ride content...
            Container(
              height: 200,
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(
                child: Text('Offer Ride Content Here'),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}