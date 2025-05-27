import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:stuber/features/map/presentation/map_component.dart';
import 'package:animated_toggle_switch/animated_toggle_switch.dart';

class RideShareScreen extends StatefulWidget {
  const RideShareScreen({Key? key}) : super(key: key);

  @override
  State<RideShareScreen> createState() => _RideShareScreenState();
}

class _RideShareScreenState extends State<RideShareScreen> {
  final MapController _mapController = MapController();
  final DraggableScrollableController _bottomSheetController = DraggableScrollableController();
  bool _isRequestingRide = false;

  // State variables for ride details
  String _startingLocation = ''; // Current Location
  String _destination = ''; //Where are you going?
  TimeOfDay? _departureTime;
  DateTime? _selectedDate;

  bool _isEditingFrom = false;
  bool _isEditingTo = false;
  final TextEditingController _startingLocationController = TextEditingController();
  final TextEditingController _destinationController = TextEditingController();
  
  // For request mode
  int _requestedSeats = 1;
  
  // For offer mode
  int _availableSeats = 3;
  int _maxDistance = 5; // in kilometers

  @override
Widget build(BuildContext context) {
  return Scaffold(
    body: Stack(
      children: [
        // Map Component
        MapComponent(
          controller: _mapController,
          onMapCreated: (GoogleMapController controller) {
            // Map is ready, you can perform initial operations here
            print('Map created successfully');
          },
        ),
        

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
        
        
        // Draggable Bottom Sheet
        DraggableScrollableSheet(
          controller: _bottomSheetController,
          initialChildSize: 0.3,
          minChildSize: 0.1,
          maxChildSize: 0.8,
          builder: (context, scrollController) {
            return Container(
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(24),
                  topRight: Radius.circular(24),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black12,
                    blurRadius: 20,
                    offset: Offset(0, -5),
                  ),
                ],
              ),
              child: Column(
                children: [
                  // Handle bar
                  Container(
                    margin: const EdgeInsets.only(top: 12, bottom: 8),
                    height: 4,
                    width: 40,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  
                  // Content
                  Expanded(
                    child: ListView(
                      controller: scrollController,
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                      children: [
                        if (_isRequestingRide) ...[
                          // Request Mode Content
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF1E88E5).withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(
                                  Icons.people_alt_rounded,
                                  color: Color(0xFF1E88E5),
                                  size: 24,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'Request a Ride',
                                    style: TextStyle(
                                      fontSize: 24,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF1A1A1A),
                                    ),
                                  ),
                                  Text(
                                    'Find someone going your way',
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.grey[600],
                                      fontWeight: FontWeight.w400,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 32),
                          
                          // Trip Details Section
                          _buildSectionHeader('Trip Details'),
                          const SizedBox(height: 16),
                          
                          // Route Container
                          Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: Colors.grey[50],
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: Colors.grey[200]!,
                                width: 1,
                              ),
                            ),
                            child: Column(
                              children: [
                                // Starting Location
                                _buildRouteItem(
                                  icon: Icons.radio_button_checked,
                                  iconColor: Colors.green,
                                  title: 'Enter Starting Location',
                                  value: _startingLocation,
                                  isEditing: _isEditingFrom,
                                  controller: _startingLocationController,
                                  onTap: () {
                                    setState(() {
                                      _isEditingFrom = true;
                                      _startingLocationController.text = _startingLocation;
                                    });
                                  },
                                  onSubmitted: () {
                                    setState(() {
                                      _startingLocation = _startingLocationController.text;
                                      _isEditingFrom = false;
                                    });
                                  },
                                ),
                                
                                // Route line
                                Container(
                                  margin: const EdgeInsets.symmetric(vertical: 8),
                                  child: Row(
                                    children: [
                                      const SizedBox(width: 32),
                                      Container(
                                        width: 2,
                                        height: 24,
                                        decoration: BoxDecoration(
                                          color: Colors.grey[300],
                                          borderRadius: BorderRadius.circular(1),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                
                                // Destination
                                _buildRouteItem(
                                  icon: Icons.location_on,
                                  iconColor: Colors.red,
                                  title: 'Enter Destination',
                                  value: _destination,
                                  isEditing: _isEditingTo,
                                  controller: _destinationController,
                                  onTap: () {
                                    setState(() {
                                      _isEditingTo = true;
                                      _destinationController.text = _destination;
                                    });
                                  },
                                  onSubmitted: () {
                                    setState(() {
                                      _destination = _destinationController.text;
                                      _isEditingTo = false;
                                    });
                                  },
                                ),
                              ],
                            ),
                          ),
                          
                          const SizedBox(height: 24),
                          
                          // Trip Preferences
                          _buildSectionHeader('Trip Preferences'),
                          const SizedBox(height: 16),
                          
                          Row(
                            children: [
                              Expanded(
                                child: _buildModernCard(
                                  icon: Icons.airline_seat_recline_normal,
                                  title: 'Passengers',
                                  value: '$_requestedSeats',
                                  subtitle: _requestedSeats == 1 ? 'person' : 'people',
                                  color: Colors.blue,
                                  onTap: () => _showSeatSelector(context),
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: _buildModernCard(
                                  icon: Icons.calendar_today,
                                  title: 'Date',
                                  value: _selectedDate != null 
                                      ? '${_selectedDate!.day}/${_selectedDate!.month}'
                                      : '--/--',
                                  subtitle: 'travel date',
                                  color: Colors.teal,
                                  onTap: () => _showDatePicker(context),
                                ),
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 16),
                          
                          Row(
                            children: [
                              Expanded(
                                child: _buildModernCard(
                                  icon: Icons.schedule,
                                  title: 'Departure',
                                  value: _departureTime?.format(context) ?? '--:--',
                                  subtitle: 'time',
                                  color: Colors.orange,
                                  onTap: () => _showTimePicker(context),
                                ),
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 32),
                          
                          // Request Ride Button
                          Container(
                            width: double.infinity,
                            height: 56,
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [Color(0xFF1E88E5), Color(0xFF1976D2)],
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                              ),
                              borderRadius: BorderRadius.circular(16),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFF1E88E5).withOpacity(0.3),
                                  blurRadius: 12,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            child: ElevatedButton(
                              onPressed: _handleRideRequest,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.transparent,
                                foregroundColor: Colors.white,
                                shadowColor: Colors.transparent,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                ),
                              ),
                              child: const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.search, size: 20),
                                  SizedBox(width: 8),
                                  Text(
                                    'Find Rides',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w600,
                                      letterSpacing: 0.5,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ] else ...[
                          // Offer Mode Content
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.green.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(
                                  Icons.directions_car_filled_rounded,
                                  color: Colors.green,
                                  size: 24,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'Offer a Ride',
                                    style: TextStyle(
                                      fontSize: 24,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF1A1A1A),
                                    ),
                                  ),
                                  Text(
                                    'Share your journey with others',
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.grey[600],
                                      fontWeight: FontWeight.w400,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 32),
                          
                          // Trip Details Section
                          _buildSectionHeader('Trip Details'),
                          const SizedBox(height: 16),
                          
                          // Route Container
                          Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: Colors.grey[50],
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: Colors.grey[200]!,
                                width: 1,
                              ),
                            ),
                            child: Column(
                              children: [
                                // Starting Location
                                _buildRouteItem(
                                  icon: Icons.radio_button_checked,
                                  iconColor: Colors.green,
                                  title: 'From',
                                  value: _startingLocation,
                                  isEditing: _isEditingFrom,
                                  controller: _startingLocationController,
                                  onTap: () {
                                    setState(() {
                                      _isEditingFrom = true;
                                      _startingLocationController.text = _startingLocation;
                                    });
                                  },
                                  onSubmitted: () {
                                    setState(() {
                                      _startingLocation = _startingLocationController.text;
                                      _isEditingFrom = false;
                                    });
                                  },
                                ),
                                
                                // Route line
                                Container(
                                  margin: const EdgeInsets.symmetric(vertical: 8),
                                  child: Row(
                                    children: [
                                      const SizedBox(width: 32),
                                      Container(
                                        width: 2,
                                        height: 24,
                                        decoration: BoxDecoration(
                                          color: Colors.grey[300],
                                          borderRadius: BorderRadius.circular(1),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                
                                // Destination
                                _buildRouteItem(
                                  icon: Icons.location_on,
                                  iconColor: Colors.red,
                                  title: 'To',
                                  value: _destination,
                                  isEditing: _isEditingTo,
                                  controller: _destinationController,
                                  onTap: () {
                                    setState(() {
                                      _isEditingTo = true;
                                      _destinationController.text = _destination;
                                    });
                                  },
                                  onSubmitted: () {
                                    setState(() {
                                      _destination = _destinationController.text;
                                      _isEditingTo = false;
                                    });
                                  },
                                ),
                              ],
                            ),
                          ),
                          
                          const SizedBox(height: 24),
                          
                          // Ride Settings
                          _buildSectionHeader('Ride Settings'),
                          const SizedBox(height: 16),
                          
                          Row(
                            children: [
                              Expanded(
                                child: _buildModernCard(
                                  icon: Icons.airline_seat_recline_normal,
                                  title: 'Seats',
                                  value: '$_availableSeats',
                                  subtitle: 'available',
                                  color: Colors.blue,
                                  onTap: () => _showAvailableSeatSelector(context),
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: _buildModernCard(
                                  icon: Icons.calendar_today,
                                  title: 'Date',
                                  value: _selectedDate != null 
                                      ? '${_selectedDate!.day}/${_selectedDate!.month}'
                                      : '--/--',
                                  subtitle: 'travel date',
                                  color: Colors.teal,
                                  onTap: () => _showDatePicker(context),
                                ),
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 16),
                          
                          Row(
                            children: [
                              Expanded(
                                child: _buildModernCard(
                                  icon: Icons.schedule,
                                  title: 'Departure',
                                  value: _departureTime?.format(context) ?? '--:--',
                                  subtitle: 'time',
                                  color: Colors.orange,
                                  onTap: () => _showTimePicker(context),
                                ),
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 16),
                          
                          _buildModernCard(
                            icon: Icons.social_distance,
                            title: 'Max Detour Distance',
                            value: '${_maxDistance}km',
                            subtitle: 'pickup/drop-off radius',
                            color: Colors.purple,
                            onTap: () => _showDistanceSelector(context),
                            isFullWidth: true,
                          ),
                          
                          const SizedBox(height: 32),
                          
                          // Offer Ride Button
                          Container(
                            width: double.infinity,
                            height: 56,
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [Colors.green, Color(0xFF4CAF50)],
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                              ),
                              borderRadius: BorderRadius.circular(16),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.green.withOpacity(0.3),
                                  blurRadius: 12,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            child: ElevatedButton(
                              onPressed: _handleRideOffer,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.transparent,
                                foregroundColor: Colors.white,
                                shadowColor: Colors.transparent,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                ),
                              ),
                              child: const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.add_circle_outline, size: 20),
                                  SizedBox(width: 8),
                                  Text(
                                    'Publish Ride',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w600,
                                      letterSpacing: 0.5,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                        
                        const SizedBox(height: 100), // Extra space at bottom
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    ),
  );
}
  
  Widget _buildSectionHeader(String title) {
    return Row(
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: Color(0xFF1A1A1A),
            letterSpacing: -0.5,
          ),
        ),
      ],
    );
  }
  
  Widget _buildRouteItem({
  required IconData icon,
  required Color iconColor,
  required String title,
  required String value,
  required bool isEditing,
  required TextEditingController controller,
  required VoidCallback onTap,
  required VoidCallback onSubmitted,
}) {
  return InkWell(
    onTap: isEditing ? null : onTap,
    borderRadius: BorderRadius.circular(12),
    child: Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(
            icon,
            color: iconColor,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey[600],
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 2),
                if (isEditing)
                  TextField(
                    controller: controller,
                    autofocus: true,
                    decoration: InputDecoration(
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.zero,
                      // hintText: 'Enter ${title.toLowerCase()}',
                      hintStyle: TextStyle(
                        fontSize: 16,
                        color: Colors.grey[400],
                      ),
                    ),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF1A1A1A),
                      letterSpacing: -0.2,
                    ),
                    textInputAction: TextInputAction.done,
                    onSubmitted: (_) => onSubmitted(),
                    onTap: () {
                      // Move cursor to end when tapped
                      controller.selection = TextSelection.fromPosition(
                        TextPosition(offset: controller.text.length),
                      );
                    },
                  )
                else
                  GestureDetector(
                    onTap: onTap,
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Text(
                        value.isEmpty ? '${title}' : value,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: value.isEmpty 
                              ? Colors.grey[400] 
                              : const Color(0xFF1A1A1A),
                          letterSpacing: -0.2,
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          GestureDetector(
            onTap: isEditing ? onSubmitted : onTap,
            child: Icon(
              isEditing ? Icons.check : Icons.edit_outlined,
              color: isEditing ? Colors.green : Colors.grey[400],
              size: 18,
            ),
          ),
        ],
      ),
    ),
  );
}
  
  Widget _buildModernCard({
    required IconData icon,
    required String title,
    required String value,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
    bool isFullWidth = false,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: Colors.grey[200]!,
            width: 1.5,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    icon,
                    color: color,
                    size: 20,
                  ),
                ),
                Icon(
                  Icons.edit_outlined,
                  color: Colors.grey[400],
                  size: 16,
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: Colors.grey[600],
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF1A1A1A),
                    letterSpacing: -0.5,
                  ),
                ),
                if (!isFullWidth) ...[
                  const SizedBox(width: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w400,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ],
            ),
            if (isFullWidth) ...[
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w400,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  void onModeChanged(bool isRequestMode) {
    setState(() {
      _isRequestingRide = isRequestMode;
    });
    
    // You can add additional logic here based on the mode
    if (isRequestMode) {
      print('Switched to Request mode');
      // Add logic for request mode
    } else {
      print('Switched to Offer mode');
      // Add logic for offer mode
    }
  }

  Widget _buildLocationTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: Colors.grey[600]),
      ),
      title: Text(
        title,
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
      subtitle: Text(subtitle),
      onTap: onTap,
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
    );
  }

  Widget _buildRideDetailCard({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: color.withOpacity(0.2),
            width: 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                icon,
                color: color,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    value,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.chevron_right,
              color: Colors.grey[400],
            ),
          ],
        ),
      ),
    );
  }

  void _showLocationPicker(BuildContext context, bool isStarting) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                isStarting ? 'Select Starting Location' : 'Select Destination',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              
              // Pre-defined locations
              _buildLocationTile(
                icon: Icons.my_location,
                title: 'Current Location',
                subtitle: 'Use GPS location',
                onTap: () {
                  setState(() {
                    if (isStarting) {
                      _startingLocation = 'Current Location';
                    } else {
                      _destination = 'Current Location';
                    }
                  });
                  Navigator.pop(context);
                },
              ),
              
              _buildLocationTile(
                icon: Icons.home,
                title: 'Home',
                subtitle: '123 Main Street, Edmonton',
                onTap: () {
                  setState(() {
                    if (isStarting) {
                      _startingLocation = 'Home';
                    } else {
                      _destination = 'Home';
                    }
                  });
                  Navigator.pop(context);
                  _mapController.animateCamera(
                    const LatLng(53.524297, -113.535773),
                  );
                },
              ),
              
              _buildLocationTile(
                icon: Icons.work,
                title: 'Work',
                subtitle: 'University of Alberta',
                onTap: () {
                  setState(() {
                    if (isStarting) {
                      _startingLocation = 'Work';
                    } else {
                      _destination = 'Work';
                    }
                  });
                  Navigator.pop(context);
                  _mapController.animateCamera(
                    const LatLng(53.523219, -113.526319),
                  );
                },
              ),
              
              _buildLocationTile(
                icon: Icons.shopping_cart,
                title: 'West Edmonton Mall',
                subtitle: '8882 170 St NW, Edmonton',
                onTap: () {
                  setState(() {
                    if (isStarting) {
                      _startingLocation = 'West Edmonton Mall';
                    } else {
                      _destination = 'West Edmonton Mall';
                    }
                  });
                  Navigator.pop(context);
                  _mapController.animateCamera(
                    const LatLng(53.522282, -113.613426),
                  );
                },
              ),
              
              const SizedBox(height: 20),
            ],
          ),
        );
      },
    );
  }

  void _showSeatSelector(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'How many seats do you need?',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [1, 2, 3, 4].map((seats) {
                  return InkWell(
                    onTap: () {
                      setState(() {
                        _requestedSeats = seats;
                      });
                      Navigator.pop(context);
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 24),
                      decoration: BoxDecoration(
                        color: Colors.blue[50],
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.blue.withOpacity(0.3)),
                      ),
                      child: Text(
                        '$seats',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 20),
            ],
          ),
        );
      },
    );
  }

  // Helper method to show available seat selector (for offer mode)
  void _showAvailableSeatSelector(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'How many seats can you offer?',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [1, 2, 3, 4, 5].map((seats) {
                  return InkWell(
                    onTap: () {
                      setState(() {
                        _availableSeats = seats;
                      });
                      Navigator.pop(context);
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 24),
                      decoration: BoxDecoration(
                        color: Colors.green[50],
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.green.withOpacity(0.3)),
                      ),
                      child: Text(
                        '$seats',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 20),
            ],
          ),
        );
      },
    );
  }

  // Helper method to show distance selector
  void _showDistanceSelector(BuildContext context) {
    final List<int> distances = [1, 2, 3, 5, 10, 15, 20];
    
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Maximum pickup/drop-off distance',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'How far are you willing to go off your route?',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              GridView.builder(
                shrinkWrap: true,
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 4,
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                  childAspectRatio: 2,
                ),
                itemCount: distances.length,
                itemBuilder: (context, index) {
                  final distance = distances[index];
                  return InkWell(
                    onTap: () {
                      setState(() {
                        _maxDistance = distance;
                      });
                      Navigator.pop(context);
                    },
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.purple[50],
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.purple.withOpacity(0.3)),
                      ),
                      child: Center(
                        child: Text(
                          '${distance}km',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 20),
            ],
          ),
        );
      },
    );
  }

  // Helper method to show time picker
  void _showTimePicker(BuildContext context) {
    showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
    ).then((time) {
      if (time != null) {
        setState(() {
          _departureTime = time;
        });
      }
    });
  }

  // Handle ride request submission
  void _handleRideRequest() {
    // Validate inputs
    if (_destination == 'Where are you going?') {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a destination')),
      );
      return;
    }
    
    if (_departureTime == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a departure time')),
      );
      return;
    }

    // Process ride request
    print('Ride Request:');
    print('From: $_startingLocation');
    print('To: $_destination');
    print('Seats: $_requestedSeats');
    print('Time: ${_departureTime!.format(context)}');
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Ride request submitted!')),
    );
  }

  // Handle ride offer submission
  void _handleRideOffer() {
    // Validate inputs
    if (_destination == 'Where are you going?') {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a destination')),
      );
      return;
    }
    
    if (_departureTime == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a departure time')),
      );
      return;
    }

    // Process ride offer
    print('Ride Offer:');
    print('From: $_startingLocation');
    print('To: $_destination');
    print('Available Seats: $_availableSeats');
    print('Time: ${_departureTime!.format(context)}');
    print('Max Distance: ${_maxDistance}km');
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Ride offer posted!')),
    );
  }

  void _showDatePicker(BuildContext context) {
    showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 30)),
    ).then((date) {
      if (date != null) {
        setState(() {
          _selectedDate = date;
        });
      }
    });
  }

  @override
  void dispose() {
    _bottomSheetController.dispose();
    _startingLocationController.dispose();
    _destinationController.dispose();
    super.dispose();
  }
}