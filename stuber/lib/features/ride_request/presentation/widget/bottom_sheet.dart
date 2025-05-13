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
import 'package:flutter/material.dart';

class RideBottomSheet extends StatefulWidget {
  final Function(bool isRequestingRide) onModeChanged;
  final Function() onConfirm;

  const RideBottomSheet({
    Key? key,
    required this.onModeChanged,
    required this.onConfirm,
  }) : super(key: key);

  @override
  State<RideBottomSheet> createState() => _RideBottomSheetState();
}

class _RideBottomSheetState extends State<RideBottomSheet> {
  final TextEditingController _currentLocationController = TextEditingController(text: "Current Location");
  final TextEditingController _destinationController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Drag handle
          Container(
            width: 40,
            height: 5,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(10),
            ),
          ),
          const SizedBox(height: 20),

          // Current Location Field
          TextFormField(
            controller: _currentLocationController,
            decoration: InputDecoration(
              prefixIcon: const Icon(Icons.my_location, color: Colors.blue),
              labelText: "Current Location",
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[100],
            ),
          ),
          const SizedBox(height: 16),

          // Destination Field
          TextFormField(
            controller: _destinationController,
            decoration: InputDecoration(
              prefixIcon: const Icon(Icons.location_on, color: Colors.red),
              labelText: "Destination",
              hintText: "Enter destination...",
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[100],
            ),
          ),
          const SizedBox(height: 24),

          // Confirm Button
          // SizedBox(
          //   width: double.infinity,
          //   child: ElevatedButton(
          //     onPressed: widget.onConfirm,
          //     style: ElevatedButton.styleFrom(
          //       backgroundColor: Theme.of(context).primaryColor,
          //       padding: const EdgeInsets.symmetric(vertical: 16),
          //       shape: RoundedRectangleBorder(
          //         borderRadius: BorderRadius.circular(30),
          //       ),
          //     ),
          //     child: const Text(
          //       'Request Ride',
          //       style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
          //     ),
          //   ),
          // ),
        ],
      ),
    );
  }
}
