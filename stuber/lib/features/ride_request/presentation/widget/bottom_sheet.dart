// import 'package:flutter/material.dart';

// class RideRequestBottomSheet extends StatefulWidget {
//   @override
//   _RideRequestBottomSheetState createState() => _RideRequestBottomSheetState();
// }

// class _RideRequestBottomSheetState extends State<RideRequestBottomSheet> {
//   final TextEditingController _pickupController = TextEditingController();
//   final TextEditingController _destinationController = TextEditingController();

//   @override
//   void dispose() {
//     _pickupController.dispose();
//     _destinationController.dispose();
//     super.dispose();
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Container(
//       decoration: BoxDecoration(
//         color: Colors.white,
//         borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
//         boxShadow: [
//           BoxShadow(
//             color: Colors.grey.withOpacity(0.3),
//             spreadRadius: 3,
//             blurRadius: 7,
//             offset: Offset(0, -3),
//           ),
//         ],
//       ),
//       child: Column(
//         mainAxisSize: MainAxisSize.min,
//         children: [
//           // Drag Handle
//           Container(
//             width: 40,
//             height: 5,
//             margin: EdgeInsets.symmetric(vertical: 12),
//             decoration: BoxDecoration(
//               color: Colors.grey.withOpacity(0.5),
//               borderRadius: BorderRadius.circular(10),
//             ),
//           ),
//           Padding(
//             padding: EdgeInsets.fromLTRB(16, 8, 16, 24),
//             child: Column(
//               crossAxisAlignment: CrossAxisAlignment.start,
//               children: [
//                 Text(
//                   'Request a Ride',
//                   style: TextStyle(
//                     fontSize: 20,
//                     fontWeight: FontWeight.bold,
//                   ),
//                 ),
//                 SizedBox(height: 16),
//                 TextField(
//                   controller: _pickupController,
//                   decoration: InputDecoration(
//                     labelText: 'Current Location',
//                     prefixIcon: Icon(Icons.my_location, color: Colors.blue),
//                     border: OutlineInputBorder(
//                       borderRadius: BorderRadius.circular(12),
//                     ),
//                     filled: true,
//                     fillColor: Colors.grey.withOpacity(0.1),
//                     contentPadding: EdgeInsets.symmetric(vertical: 12, horizontal: 16),
//                   ),
//                 ),
//                 SizedBox(height: 16),
//                 TextField(
//                   controller: _destinationController,
//                   decoration: InputDecoration(
//                     labelText: 'Destination',
//                     prefixIcon: Icon(Icons.location_on, color: Colors.red),
//                     border: OutlineInputBorder(
//                       borderRadius: BorderRadius.circular(12),
//                     ),
//                     filled: true,
//                     fillColor: Colors.grey.withOpacity(0.1),
//                     contentPadding: EdgeInsets.symmetric(vertical: 12, horizontal: 16),
//                   ),
//                 ),
//                 SizedBox(height: 24),
//               ],
//             ),
//           ),
//         ],
//       ),
//     );
//   }
// }

// // How to show the bottom sheet:
// // void showRideRequestSheet(BuildContext context) {
// //   showModalBottomSheet(
// //     context: context,
// //     isScrollControlled: true,
// //     backgroundColor: Colors.transparent,
// //     builder: (context) => DraggableScrollableSheet(
// //       initialChildSize: 0.5,
// //       minChildSize: 0.2,
// //       maxChildSize: 0.9,
// //       builder: (_, scrollController) {
// //         return SingleChildScrollView(
// //           controller: scrollController,
// //           child: RideRequestBottomSheet(),
// //         );
// //       },
// //     ),
// //   );
// // }
// import 'package:flutter/material.dart';

// class RideBottomSheet extends StatefulWidget {
//   final Function(bool isRequestingRide) onModeChanged;
//   final Function() onConfirm;

//   const RideBottomSheet({
//     Key? key,
//     required this.onModeChanged,
//     required this.onConfirm,
//   }) : super(key: key);

//   @override
//   State<RideBottomSheet> createState() => _RideBottomSheetState();
// }

// class _RideBottomSheetState extends State<RideBottomSheet> {
//   final TextEditingController _currentLocationController = TextEditingController(text: "Current Location");
//   final TextEditingController _destinationController = TextEditingController();

//   @override
//   Widget build(BuildContext context) {
//     return Container(
//       padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
//       decoration: BoxDecoration(
//         color: Colors.white,
//         borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
//         boxShadow: [
//           BoxShadow(
//             color: Colors.black.withOpacity(0.08),
//             blurRadius: 12,
//             offset: const Offset(0, -2),
//           ),
//         ],
//       ),
//       child: Column(
//         mainAxisSize: MainAxisSize.min,
//         children: [
//           // Drag handle
//           Container(
//             width: 40,
//             height: 5,
//             decoration: BoxDecoration(
//               color: Colors.grey[300],
//               borderRadius: BorderRadius.circular(10),
//             ),
//           ),
//           const SizedBox(height: 20),

//           // Current Location Field
//           TextFormField(
//             controller: _currentLocationController,
//             decoration: InputDecoration(
//               prefixIcon: const Icon(Icons.my_location, color: Colors.blue),
//               labelText: "Current Location",
//               border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
//               filled: true,
//               fillColor: Colors.grey[100],
//             ),
//           ),
//           const SizedBox(height: 16),

//           // Destination Field
//           TextFormField(
//             controller: _destinationController,
//             decoration: InputDecoration(
//               prefixIcon: const Icon(Icons.location_on, color: Colors.red),
//               labelText: "Destination",
//               hintText: "Enter destination...",
//               border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
//               filled: true,
//               fillColor: Colors.grey[100],
//             ),
//           ),
//           const SizedBox(height: 24),

//           // Confirm Button
//           // SizedBox(
//           //   width: double.infinity,
//           //   child: ElevatedButton(
//           //     onPressed: widget.onConfirm,
//           //     style: ElevatedButton.styleFrom(
//           //       backgroundColor: Theme.of(context).primaryColor,
//           //       padding: const EdgeInsets.symmetric(vertical: 16),
//           //       shape: RoundedRectangleBorder(
//           //         borderRadius: BorderRadius.circular(30),
//           //       ),
//           //     ),
//           //     child: const Text(
//           //       'Request Ride',
//           //       style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
//           //     ),
//           //   ),
//           // ),
//         ],
//       ),
//     );
//   }
// }



// import 'package:flutter/material.dart';

// class RideBottomSheet extends StatefulWidget {
//   final Function(bool isRequestingRide) onModeChanged;
//   final Function() onConfirmRequest;
//   final Function() onConfirmOffer;
//   final ScrollController scrollController;
//   final bool isRequestingRide;

//   const RideBottomSheet({
//     Key? key,
//     required this.onModeChanged,
//     required this.onConfirmRequest,
//     required this.onConfirmOffer,
//     required this.scrollController,
//     required this.isRequestingRide,
//   }) : super(key: key);

//   @override
//   State<RideBottomSheet> createState() => _RideBottomSheetState();
// }

// class _RideBottomSheetState extends State<RideBottomSheet> {
//   // Controllers for request ride mode
//   final TextEditingController _currentLocationController = TextEditingController(text: "Current Location");
//   final TextEditingController _destinationController = TextEditingController();
  
//   // Controllers for offer ride mode
//   final TextEditingController _startLocationController = TextEditingController();
//   final TextEditingController _endLocationController = TextEditingController();
//   final TextEditingController _departureTimeController = TextEditingController();
//   final TextEditingController _priceController = TextEditingController();
  
//   // State variables
//   int _passengerCount = 1;
//   int _availableSeats = 3;

//   @override
//   void dispose() {
//     _currentLocationController.dispose();
//     _destinationController.dispose();
//     _startLocationController.dispose();
//     _endLocationController.dispose();
//     _departureTimeController.dispose();
//     _priceController.dispose();
//     super.dispose();
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Container(
//       padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
//       decoration: BoxDecoration(
//         color: Colors.white,
//         borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
//         boxShadow: [
//           BoxShadow(
//             color: Colors.black.withOpacity(0.08),
//             blurRadius: 12,
//             offset: const Offset(0, -2),
//           ),
//         ],
//       ),
//       child: widget.isRequestingRide 
//           ? _buildRequestRideContent() 
//           : _buildOfferRideContent(),
//     );
//   }

//   // Content for requesting a ride
//   Widget _buildRequestRideContent() {
//     return ListView(
//       controller: widget.scrollController,
//       shrinkWrap: true,
//       children: [
//         // Drag handle
//         Center(
//           child: Container(
//             width: 40,
//             height: 5,
//             decoration: BoxDecoration(
//               color: Colors.grey[300],
//               borderRadius: BorderRadius.circular(10),
//             ),
//           ),
//         ),
//         const SizedBox(height: 20),
        
//         // Title
//         const Text(
//           'Request a Ride',
//           style: TextStyle(
//             fontSize: 22,
//             fontWeight: FontWeight.bold,
//           ),
//         ),
//         const SizedBox(height: 20),
        
//         // Current Location Field
//         TextFormField(
//           controller: _currentLocationController,
//           decoration: InputDecoration(
//             prefixIcon: const Icon(Icons.my_location, color: Colors.blue),
//             labelText: "Current Location",
//             border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
//             filled: true,
//             fillColor: Colors.grey[100],
//           ),
//         ),
//         const SizedBox(height: 16),
        
//         // Destination Field
//         TextFormField(
//           controller: _destinationController,
//           decoration: InputDecoration(
//             prefixIcon: const Icon(Icons.location_on, color: Colors.red),
//             labelText: "Destination",
//             hintText: "Enter destination...",
//             border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
//             filled: true,
//             fillColor: Colors.grey[100],
//           ),
//         ),
//         const SizedBox(height: 24),
        
//         // Number of passengers
//         Row(
//           children: [
//             const Icon(Icons.people, color: Colors.blue),
//             const SizedBox(width: 10),
//             const Text(
//               'Passengers:',
//               style: TextStyle(
//                 fontSize: 16,
//                 fontWeight: FontWeight.w500,
//               ),
//             ),
//             const Spacer(),
//             Container(
//               decoration: BoxDecoration(
//                 color: Colors.grey[100],
//                 borderRadius: BorderRadius.circular(8),
//               ),
//               padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
//               child: DropdownButton<int>(
//                 value: _passengerCount,
//                 underline: const SizedBox(),
//                 items: [1, 2, 3, 4].map((int value) {
//                   return DropdownMenuItem<int>(
//                     value: value,
//                     child: Text('$value'),
//                   );
//                 }).toList(),
//                 onChanged: (newValue) {
//                   setState(() {
//                     _passengerCount = newValue!;
//                   });
//                 },
//               ),
//             ),
//           ],
//         ),
//         const SizedBox(height: 30),
        
//         // Confirm Button
//         SizedBox(
//           width: double.infinity,
//           child: ElevatedButton(
//             onPressed: widget.onConfirmRequest,
//             style: ElevatedButton.styleFrom(
//               backgroundColor: Theme.of(context).primaryColor,
//               padding: const EdgeInsets.symmetric(vertical: 16),
//               shape: RoundedRectangleBorder(
//                 borderRadius: BorderRadius.circular(30),
//               ),
//             ),
//             child: const Text(
//               'Request Ride',
//               style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
//             ),
//           ),
//         ),
//       ],
//     );
//   }

//   // Content for offering a ride
//   Widget _buildOfferRideContent() {
//     return ListView(
//       controller: widget.scrollController,
//       shrinkWrap: true,
//       children: [
//         // Drag handle
//         Center(
//           child: Container(
//             width: 40,
//             height: 5,
//             decoration: BoxDecoration(
//               color: Colors.grey[300],
//               borderRadius: BorderRadius.circular(10),
//             ),
//           ),
//         ),
//         const SizedBox(height: 20),
        
//         // Title
//         const Text(
//           'Offer a Ride',
//           style: TextStyle(
//             fontSize: 22,
//             fontWeight: FontWeight.bold,
//           ),
//         ),
//         const SizedBox(height: 20),
        
//         // Starting location
//         TextFormField(
//           controller: _startLocationController,
//           decoration: InputDecoration(
//             prefixIcon: const Icon(Icons.my_location, color: Colors.blue),
//             labelText: "Starting from",
//             hintText: "Enter your starting location...",
//             border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
//             filled: true,
//             fillColor: Colors.grey[100],
//           ),
//         ),
//         const SizedBox(height: 16),
        
//         // Destination
//         TextFormField(
//           controller: _endLocationController,
//           decoration: InputDecoration(
//             prefixIcon: const Icon(Icons.location_on, color: Colors.red),
//             labelText: "Destination",
//             hintText: "Enter your destination...",
//             border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
//             filled: true,
//             fillColor: Colors.grey[100],
//           ),
//         ),
//         const SizedBox(height: 16),
        
//         // Departure time
//         TextFormField(
//           controller: _departureTimeController,
//           decoration: InputDecoration(
//             prefixIcon: const Icon(Icons.access_time, color: Colors.blue),
//             labelText: "Departure Time",
//             hintText: "When are you leaving?",
//             border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
//             filled: true,
//             fillColor: Colors.grey[100],
//           ),
//           onTap: () async {
//             // Show time picker when field is tapped
//             final TimeOfDay? pickedTime = await showTimePicker(
//               context: context,
//               initialTime: TimeOfDay.now(),
//             );
            
//             if (pickedTime != null) {
//               setState(() {
//                 _departureTimeController.text = pickedTime.format(context);
//               });
//             }
//           },
//         ),
//         const SizedBox(height: 24),
        
//         // Available seats
//         Row(
//           children: [
//             const Icon(Icons.event_seat, color: Colors.blue),
//             const SizedBox(width: 10),
//             const Text(
//               'Available seats:',
//               style: TextStyle(
//                 fontSize: 16,
//                 fontWeight: FontWeight.w500,
//               ),
//             ),
//             const Spacer(),
//             Container(
//               decoration: BoxDecoration(
//                 color: Colors.grey[100],
//                 borderRadius: BorderRadius.circular(8),
//               ),
//               padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
//               child: DropdownButton<int>(
//                 value: _availableSeats,
//                 underline: const SizedBox(),
//                 items: [1, 2, 3, 4].map((int value) {
//                   return DropdownMenuItem<int>(
//                     value: value,
//                     child: Text('$value'),
//                   );
//                 }).toList(),
//                 onChanged: (newValue) {
//                   setState(() {
//                     _availableSeats = newValue!;
//                   });
//                 },
//               ),
//             ),
//           ],
//         ),
//         const SizedBox(height: 16),
        
//         // Price per seat
//         TextFormField(
//           controller: _priceController,
//           keyboardType: TextInputType.number,
//           decoration: InputDecoration(
//             prefixIcon: const Icon(Icons.attach_money, color: Colors.green),
//             labelText: "Price per seat",
//             hintText: "How much will you charge?",
//             border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
//             filled: true,
//             fillColor: Colors.grey[100],
//           ),
//         ),
//         const SizedBox(height: 30),
        
//         // Confirm Button
//         SizedBox(
//           width: double.infinity,
//           child: ElevatedButton(
//             onPressed: widget.onConfirmOffer,
//             style: ElevatedButton.styleFrom(
//               backgroundColor: Theme.of(context).primaryColor,
//               padding: const EdgeInsets.symmetric(vertical: 16),
//               shape: RoundedRectangleBorder(
//                 borderRadius: BorderRadius.circular(30),
//               ),
//             ),
//             child: const Text(
//               'Offer Ride',
//               style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
//             ),
//           ),
//         ),
//       ],
//     );
//   }
// }






// import 'package:flutter/material.dart';

// class RideBottomSheet extends StatefulWidget {
//   final Function(bool isRequestingRide) onModeChanged;
//   final Function() onConfirmRequest;
//   final Function() onConfirmOffer;
//   final ScrollController scrollController;
//   final bool isRequestingRide;

//   const RideBottomSheet({
//     Key? key,
//     required this.onModeChanged,
//     required this.onConfirmRequest,
//     required this.onConfirmOffer,
//     required this.scrollController,
//     required this.isRequestingRide,
//   }) : super(key: key);

//   @override
//   State<RideBottomSheet> createState() => _RideBottomSheetState();
// }

// class _RideBottomSheetState extends State<RideBottomSheet>
//     with TickerProviderStateMixin {
//   // Controllers for request ride mode
//   final TextEditingController _currentLocationController = 
//       TextEditingController(text: "Current Location");
//   final TextEditingController _destinationController = TextEditingController();
  
//   // Controllers for offer ride mode
//   final TextEditingController _startLocationController = TextEditingController();
//   final TextEditingController _endLocationController = TextEditingController();
//   final TextEditingController _departureTimeController = TextEditingController();
//   final TextEditingController _priceController = TextEditingController();
  
//   // State variables
//   int _passengerCount = 1;
//   int _availableSeats = 3;
  
//   // Animation controllers
//   late AnimationController _fadeController;
//   late Animation<double> _fadeAnimation;

//   @override
//   void initState() {
//     super.initState();
//     _fadeController = AnimationController(
//       duration: const Duration(milliseconds: 300),
//       vsync: this,
//     );
//     _fadeAnimation = CurvedAnimation(
//       parent: _fadeController,
//       curve: Curves.easeInOut,
//     );
//     _fadeController.forward();
//   }

//   @override
//   void dispose() {
//     _currentLocationController.dispose();
//     _destinationController.dispose();
//     _startLocationController.dispose();
//     _endLocationController.dispose();
//     _departureTimeController.dispose();
//     _priceController.dispose();
//     _fadeController.dispose();
//     super.dispose();
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Container(
//       decoration: BoxDecoration(
//         color: Colors.white,
//         borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
//         boxShadow: [
//           BoxShadow(
//             color: Colors.black.withOpacity(0.1),
//             blurRadius: 20,
//             offset: const Offset(0, -5),
//           ),
//         ],
//       ),
//       child: Column(
//         mainAxisSize: MainAxisSize.min,
//         children: [
//           _buildHeader(),
//           Flexible(
//             child: FadeTransition(
//               opacity: _fadeAnimation,
//               child: widget.isRequestingRide 
//                   ? _buildRequestRideContent() 
//                   : _buildOfferRideContent(),
//             ),
//           ),
//         ],
//       ),
//     );
//   }

//   Widget _buildHeader() {
//     return Container(
//       padding: const EdgeInsets.fromLTRB(20, 16, 20, 0), // Removed bottom padding completely
//       child: Column(
//         children: [
//           // Drag handle
//           Container(
//             width: 50,
//             height: 5,
//             decoration: BoxDecoration(
//               color: Colors.grey[300],
//               borderRadius: BorderRadius.circular(3),
//             ),
//           ),
          
//           // Toggle buttons
//           // Container(
//           //   decoration: BoxDecoration(
//           //     color: Colors.grey[100],
//           //     borderRadius: BorderRadius.circular(25),
//           //   ),
//           //   padding: const EdgeInsets.all(4),
//           //   child: Row(
//           //     children: [
//           //       Expanded(
//           //         child: _buildToggleButton(
//           //           'Request Ride',
//           //           widget.isRequestingRide,
//           //           () => widget.onModeChanged(true),
//           //           Icons.directions_car,
//           //         ),
//           //       ),
//           //       Expanded(
//           //         child: _buildToggleButton(
//           //           'Offer Ride',
//           //           !widget.isRequestingRide,
//           //           () => widget.onModeChanged(false),
//           //           Icons.car_rental,
//           //         ),
//           //       ),
//           //     ],
//           //   ),
//           // ),
//         ],
//       ),
//     );
//   }

//   Widget _buildToggleButton(
//     String text,
//     bool isSelected,
//     VoidCallback onTap,
//     IconData icon,
//   ) {
//     return GestureDetector(
//       onTap: () {
//         onTap();
//         _fadeController.reset();
//         _fadeController.forward();
//       },
//       child: AnimatedContainer(
//         duration: const Duration(milliseconds: 200),
//         padding: const EdgeInsets.symmetric(vertical: 12),
//         decoration: BoxDecoration(
//           color: isSelected ? Theme.of(context).primaryColor : Colors.transparent,
//           borderRadius: BorderRadius.circular(20),
//           boxShadow: isSelected ? [
//             BoxShadow(
//               color: Theme.of(context).primaryColor.withOpacity(0.3),
//               blurRadius: 8,
//               offset: const Offset(0, 2),
//             ),
//           ] : null,
//         ),
//         child: Row(
//           mainAxisAlignment: MainAxisAlignment.center,
//           children: [
//             Icon(
//               icon,
//               color: isSelected ? Colors.white : Colors.grey[600],
//               size: 18,
//             ),
//             const SizedBox(width: 6),
//             Text(
//               text,
//               style: TextStyle(
//                 color: isSelected ? Colors.white : Colors.grey[600],
//                 fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
//                 fontSize: 14,
//               ),
//             ),
//           ],
//         ),
//       ),
//     );
//   }

//   Widget _buildRequestRideContent() {
//     return Padding(
//       padding: const EdgeInsets.symmetric(horizontal: 20),
//       child: ListView(
//         controller: widget.scrollController,
//         shrinkWrap: true,
//         physics: const NeverScrollableScrollPhysics(),
//         children: [
//           const SizedBox(height: 16), // Keep minimal spacing for visual balance
          
//           // Trip details card
//           _buildCard(
//             child: Column(
//               crossAxisAlignment: CrossAxisAlignment.start,
//               children: [
//                 _buildSectionTitle('Trip Details', Icons.route),
//                 const SizedBox(height: 16),
                
//                 _buildEnhancedTextField(
//                   controller: _currentLocationController,
//                   icon: Icons.my_location,
//                   iconColor: Colors.blue,
//                   label: "From",
//                   readOnly: true,
//                 ),
//                 const SizedBox(height: 16),
                
//                 _buildEnhancedTextField(
//                   controller: _destinationController,
//                   icon: Icons.location_on,
//                   iconColor: Colors.red,
//                   label: "To",
//                   hint: "Where are you going?",
//                 ),
//               ],
//             ),
//           ),
          
//           const SizedBox(height: 16),
          
//           // Preferences card
//           _buildCard(
//             child: Column(
//               crossAxisAlignment: CrossAxisAlignment.start,
//               children: [
//                 _buildSectionTitle('Preferences', Icons.tune),
//                 const SizedBox(height: 16),
                
//                 _buildPassengerSelector(),
//               ],
//             ),
//           ),
          
//           const SizedBox(height: 24),
          
//           // Action button
//           _buildActionButton(
//             'Find My Ride',
//             Icons.search,
//             widget.onConfirmRequest,
//             Colors.blue,
//           ),
          
//           const SizedBox(height: 20),
//         ],
//       ),
//     );
//   }

//   Widget _buildOfferRideContent() {
//     return Padding(
//       padding: const EdgeInsets.symmetric(horizontal: 20),
//       child: ListView(
//         controller: widget.scrollController,
//         shrinkWrap: true,
//         physics: const NeverScrollableScrollPhysics(),
//         children: [
//           const SizedBox(height: 16), // Keep minimal spacing for visual balance
          
//           // Route details card
//           _buildCard(
//             child: Column(
//               crossAxisAlignment: CrossAxisAlignment.start,
//               children: [
//                 _buildSectionTitle('Route Details', Icons.route),
//                 const SizedBox(height: 16),
                
//                 _buildEnhancedTextField(
//                   controller: _startLocationController,
//                   icon: Icons.my_location,
//                   iconColor: Colors.blue,
//                   label: "From",
//                   hint: "Starting location",
//                 ),
//                 const SizedBox(height: 16),
                
//                 _buildEnhancedTextField(
//                   controller: _endLocationController,
//                   icon: Icons.location_on,
//                   iconColor: Colors.red,
//                   label: "To",
//                   hint: "Final destination",
//                 ),
//               ],
//             ),
//           ),
          
//           const SizedBox(height: 16),
          
//           // Trip information card
//           _buildCard(
//             child: Column(
//               crossAxisAlignment: CrossAxisAlignment.start,
//               children: [
//                 _buildSectionTitle('Trip Information', Icons.info_outline),
//                 const SizedBox(height: 16),
                
//                 _buildTimeSelector(),
//                 const SizedBox(height: 16),
                
//                 Row(
//                   children: [
//                     Expanded(child: _buildSeatsSelector()),
//                     const SizedBox(width: 12),
//                     Expanded(
//                       child: _buildEnhancedTextField(
//                         controller: _priceController,
//                         icon: Icons.attach_money,
//                         iconColor: Colors.green,
//                         label: "Price/seat",
//                         hint: "0",
//                         keyboardType: TextInputType.number,
//                       ),
//                     ),
//                   ],
//                 ),
//               ],
//             ),
//           ),
          
//           const SizedBox(height: 24),
          
//           // Action button
//           _buildActionButton(
//             'Publish Ride',
//             Icons.publish,
//             widget.onConfirmOffer,
//             Colors.green,
//           ),
          
//           const SizedBox(height: 20),
//         ],
//       ),
//     );
//   }

//   Widget _buildCard({required Widget child}) {
//     return Container(
//       padding: const EdgeInsets.all(20),
//       decoration: BoxDecoration(
//         color: Colors.white,
//         borderRadius: BorderRadius.circular(16),
//         border: Border.all(color: Colors.grey[200]!),
//         boxShadow: [
//           BoxShadow(
//             color: Colors.grey.withOpacity(0.08),
//             blurRadius: 10,
//             offset: const Offset(0, 2),
//           ),
//         ],
//       ),
//       child: child,
//     );
//   }

//   Widget _buildSectionTitle(String title, IconData icon) {
//     return Row(
//       children: [
//         Container(
//           padding: const EdgeInsets.all(8),
//           decoration: BoxDecoration(
//             color: Theme.of(context).primaryColor.withOpacity(0.1),
//             borderRadius: BorderRadius.circular(8),
//           ),
//           child: Icon(
//             icon,
//             color: Theme.of(context).primaryColor,
//             size: 20,
//           ),
//         ),
//         const SizedBox(width: 12),
//         Text(
//           title,
//           style: const TextStyle(
//             fontSize: 16,
//             fontWeight: FontWeight.w600,
//             color: Colors.black87,
//           ),
//         ),
//       ],
//     );
//   }

//   Widget _buildEnhancedTextField({
//     required TextEditingController controller,
//     required IconData icon,
//     required Color iconColor,
//     required String label,
//     String? hint,
//     bool readOnly = false,
//     TextInputType? keyboardType,
//   }) {
//     return Container(
//       decoration: BoxDecoration(
//         color: Colors.grey[50],
//         borderRadius: BorderRadius.circular(12),
//         border: Border.all(color: Colors.grey[200]!),
//       ),
//       child: TextFormField(
//         controller: controller,
//         readOnly: readOnly,
//         keyboardType: keyboardType,
//         decoration: InputDecoration(
//           prefixIcon: Container(
//             margin: const EdgeInsets.all(12),
//             decoration: BoxDecoration(
//               color: iconColor.withOpacity(0.1),
//               borderRadius: BorderRadius.circular(8),
//             ),
//             child: Icon(icon, color: iconColor, size: 20),
//           ),
//           labelText: label,
//           hintText: hint,
//           border: InputBorder.none,
//           contentPadding: const EdgeInsets.symmetric(vertical: 16),
//           labelStyle: TextStyle(
//             color: Colors.grey[600],
//             fontWeight: FontWeight.w500,
//           ),
//           hintStyle: TextStyle(color: Colors.grey[400]),
//         ),
//       ),
//     );
//   }

//   Widget _buildPassengerSelector() {
//     return Container(
//       padding: const EdgeInsets.all(16),
//       decoration: BoxDecoration(
//         color: Colors.grey[50],
//         borderRadius: BorderRadius.circular(12),
//         border: Border.all(color: Colors.grey[200]!),
//       ),
//       child: Row(
//         children: [
//           Container(
//             padding: const EdgeInsets.all(8),
//             decoration: BoxDecoration(
//               color: Colors.blue.withOpacity(0.1),
//               borderRadius: BorderRadius.circular(8),
//             ),
//             child: const Icon(Icons.people, color: Colors.blue, size: 20),
//           ),
//           const SizedBox(width: 12),
//           const Text(
//             'Passengers',
//             style: TextStyle(
//               fontSize: 14,
//               fontWeight: FontWeight.w500,
//               color: Colors.black87,
//             ),
//           ),
//           const Spacer(),
//           Container(
//             decoration: BoxDecoration(
//               color: Colors.white,
//               borderRadius: BorderRadius.circular(8),
//               border: Border.all(color: Colors.grey[300]!),
//             ),
//             child: Row(
//               mainAxisSize: MainAxisSize.min,
//               children: [
//                 IconButton(
//                   onPressed: _passengerCount > 1
//                       ? () => setState(() => _passengerCount--)
//                       : null,
//                   icon: const Icon(Icons.remove, size: 18),
//                   padding: const EdgeInsets.all(4),
//                   constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
//                 ),
//                 Container(
//                   padding: const EdgeInsets.symmetric(horizontal: 16),
//                   child: Text(
//                     '$_passengerCount',
//                     style: const TextStyle(
//                       fontSize: 16,
//                       fontWeight: FontWeight.w600,
//                     ),
//                   ),
//                 ),
//                 IconButton(
//                   onPressed: _passengerCount < 4
//                       ? () => setState(() => _passengerCount++)
//                       : null,
//                   icon: const Icon(Icons.add, size: 18),
//                   padding: const EdgeInsets.all(4),
//                   constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
//                 ),
//               ],
//             ),
//           ),
//         ],
//       ),
//     );
//   }

//   Widget _buildTimeSelector() {
//     return Container(
//       decoration: BoxDecoration(
//         color: Colors.grey[50],
//         borderRadius: BorderRadius.circular(12),
//         border: Border.all(color: Colors.grey[200]!),
//       ),
//       child: TextFormField(
//         controller: _departureTimeController,
//         readOnly: true,
//         decoration: InputDecoration(
//           prefixIcon: Container(
//             margin: const EdgeInsets.all(12),
//             decoration: BoxDecoration(
//               color: Colors.orange.withOpacity(0.1),
//               borderRadius: BorderRadius.circular(8),
//             ),
//             child: const Icon(Icons.schedule, color: Colors.orange, size: 20),
//           ),
//           labelText: "Departure Time",
//           hintText: "Select departure time",
//           border: InputBorder.none,
//           contentPadding: const EdgeInsets.symmetric(vertical: 16),
//           labelStyle: TextStyle(
//             color: Colors.grey[600],
//             fontWeight: FontWeight.w500,
//           ),
//           hintStyle: TextStyle(color: Colors.grey[400]),
//         ),
//         onTap: () async {
//           final DateTime? pickedDate = await showDatePicker(
//             context: context,
//             initialDate: DateTime.now(),
//             firstDate: DateTime.now(),
//             lastDate: DateTime.now().add(const Duration(days: 30)),
//           );
          
//           if (pickedDate != null) {
//             final TimeOfDay? pickedTime = await showTimePicker(
//               context: context,
//               initialTime: TimeOfDay.now(),
//             );
            
//             if (pickedTime != null) {
//               setState(() {
//                 _departureTimeController.text = 
//                     '${pickedDate.day}/${pickedDate.month} at ${pickedTime.format(context)}';
//               });
//             }
//           }
//         },
//       ),
//     );
//   }

//   Widget _buildSeatsSelector() {
//     return Container(
//       padding: const EdgeInsets.all(16),
//       decoration: BoxDecoration(
//         color: Colors.grey[50],
//         borderRadius: BorderRadius.circular(12),
//         border: Border.all(color: Colors.grey[200]!),
//       ),
//       child: Column(
//         crossAxisAlignment: CrossAxisAlignment.start,
//         children: [
//           Row(
//             children: [
//               Container(
//                 padding: const EdgeInsets.all(6),
//                 decoration: BoxDecoration(
//                   color: Colors.purple.withOpacity(0.1),
//                   borderRadius: BorderRadius.circular(6),
//                 ),
//                 child: const Icon(Icons.event_seat, color: Colors.purple, size: 16),
//               ),
//               const SizedBox(width: 8),
//               Text(
//                 'Available Seats',
//                 style: TextStyle(
//                   fontSize: 12,
//                   fontWeight: FontWeight.w500,
//                   color: Colors.grey[600],
//                 ),
//               ),
//             ],
//           ),
//           const SizedBox(height: 8),
//           Row(
//             children: [
//               Container(
//                 decoration: BoxDecoration(
//                   color: Colors.white,
//                   borderRadius: BorderRadius.circular(8),
//                   border: Border.all(color: Colors.grey[300]!),
//                 ),
//                 child: Row(
//                   mainAxisSize: MainAxisSize.min,
//                   children: [
//                     IconButton(
//                       onPressed: _availableSeats > 1
//                           ? () => setState(() => _availableSeats--)
//                           : null,
//                       icon: const Icon(Icons.remove, size: 16),
//                       padding: const EdgeInsets.all(4),
//                       constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
//                     ),
//                     Container(
//                       padding: const EdgeInsets.symmetric(horizontal: 12),
//                       child: Text(
//                         '$_availableSeats',
//                         style: const TextStyle(
//                           fontSize: 14,
//                           fontWeight: FontWeight.w600,
//                         ),
//                       ),
//                     ),
//                     IconButton(
//                       onPressed: _availableSeats < 4
//                           ? () => setState(() => _availableSeats++)
//                           : null,
//                       icon: const Icon(Icons.add, size: 16),
//                       padding: const EdgeInsets.all(4),
//                       constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
//                     ),
//                   ],
//                 ),
//               ),
//             ],
//           ),
//         ],
//       ),
//     );
//   }

//   Widget _buildActionButton(
//     String text,
//     IconData icon,
//     VoidCallback onPressed,
//     Color color,
//   ) {
//     return Container(
//       width: double.infinity,
//       decoration: BoxDecoration(
//         boxShadow: [
//           BoxShadow(
//             color: color.withOpacity(0.3),
//             blurRadius: 12,
//             offset: const Offset(0, 4),
//           ),
//         ],
//       ),
//       child: ElevatedButton(
//         onPressed: onPressed,
//         style: ElevatedButton.styleFrom(
//           backgroundColor: color,
//           foregroundColor: Colors.white,
//           padding: const EdgeInsets.symmetric(vertical: 18),
//           shape: RoundedRectangleBorder(
//             borderRadius: BorderRadius.circular(16),
//           ),
//           elevation: 0,
//         ),
//         child: Row(
//           mainAxisAlignment: MainAxisAlignment.center,
//           children: [
//             Icon(icon, size: 20),
//             const SizedBox(width: 8),
//             Text(
//               text,
//               style: const TextStyle(
//                 fontSize: 16,
//                 fontWeight: FontWeight.w600,
//               ),
//             ),
//           ],
//         ),
//       ),
//     );
//   }
// }


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