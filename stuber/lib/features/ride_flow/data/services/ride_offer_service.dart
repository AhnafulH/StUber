import 'package:flutter/material.dart';
import '../models/ride_offer_model.dart';
import '../repositories/ride_offer_repository.dart';

class RideOfferService {
  final RideOfferRepository _repository = RideOfferRepository();

  /// Create ride offer from your form data
  Future<RideOfferModel> createRideOfferFromForm({
    required String startingLocation,
    required String destination,
    required int seatsAvailable,
    required DateTime selectedDate,
    required TimeOfDay departureTime,
    required int maxDetourDistance,
    double? startingLatitude,
    double? startingLongitude,
    double? destinationLatitude,
    double? destinationLongitude,
  }) async {
    
    print('🎯 RideOfferService: Creating ride offer...');
    
    // 1. Basic validation
    // _validateInput(
    //   startingLocation: startingLocation,
    //   destination: destination,
    //   seatsAvailable: seatsAvailable,
    //   selectedDate: selectedDate,
    //   departureTime: departureTime,
    //   maxDetourDistance: maxDetourDistance,
    // );

    // 2. Combine date and time
    final departureDateTime = DateTime(
      selectedDate.year,
      selectedDate.month,
      selectedDate.day,
      departureTime.hour,
      departureTime.minute,
    );

    print('📅 Departure: $departureDateTime');

    // 3. Create the model
    final offer = RideOfferModel(
      startingLocation: startingLocation.trim(),
      startingLatitude: startingLatitude,
      startingLongitude: startingLongitude,
      destination: destination.trim(),
      destinationLatitude: destinationLatitude,
      destinationLongitude: destinationLongitude,
      seatsAvailable: seatsAvailable,
      departureDateTime: departureDateTime,
      maxDetourDistance: maxDetourDistance,
    );

    print('🚗 Created ride offer: $offer');

    // 4. Save to database
    return await _repository.createRideOffer(offer);
  }

  /// Get all ride offers (for testing/admin)
  // Future<List<RideOfferModel>> getAllRideOffers() async {
  //   return await _repository.getAllRideOffers();
  // }

  /// Get available ride offers (for passengers to see)
  // Future<List<RideOfferModel>> getAvailableRideOffers() async {
  //   return await _repository.getAvailableRideOffers();
  // }

  /// Search ride offers with filters
  // Future<List<RideOfferModel>> searchRideOffers({
  //   String? startingLocation,
  //   String? destination,
  //   DateTime? departureDate,
  //   int? minSeats,
  // }) async {
  //   return await _repository.searchRideOffers(
  //     startingLocation: startingLocation,
  //     destination: destination,
  //     departureDate: departureDate,
  //     minSeats: minSeats,
  //   );
  // }

  /// Book a seat (reduce available seats)
  // Future<RideOffer> bookSeat(int offerId, int seatsToBook) async {
  //   // Get current offer
  //   final offers = await _repository.getAllRideOffers();
  //   final offer = offers.firstWhere((o) => o.id == offerId);
    
  //   // Validate booking
  //   if (offer.seatsAvailable < seatsToBook) {
  //     throw ValidationException('Not enough seats available. Only ${offer.seatsAvailable} seats left.');
  //   }
    
  //   if (offer.isExpired) {
  //     throw ValidationException('This ride offer has expired.');
  //   }
    
  //   // Update available seats
  //   final newSeatsAvailable = offer.seatsAvailable - seatsToBook;
  //   return await _repository.updateRideOffer(offerId, {
  //     'seats_available': newSeatsAvailable,
  //   });
  // }

  /// Cancel ride offer
  // Future<void> cancelRideOffer(int offerId) async {
  //   await _repository.deleteRideOffer(offerId);
  // }

  /// Test if database is working
  Future<bool> testDatabaseConnection() async {
    return await _repository.testConnection();
  }

  /// Validate form input for ride offers
  // void _validateInput({
  //   required String startingLocation,
  //   required String destination,
  //   required int seatsAvailable,
  //   required DateTime selectedDate,
  //   required TimeOfDay departureTime,
  //   required int maxDetourDistance,
  // }) {
  //   // Check starting location
  //   if (startingLocation.trim().isEmpty) {
  //     throw ValidationException('Starting location cannot be empty');
  //   }

  //   // Check destination
  //   if (destination.trim().isEmpty) {
  //     throw ValidationException('Destination cannot be empty');
  //   }

  //   // Check if they're the same
  //   if (startingLocation.trim().toLowerCase() == destination.trim().toLowerCase()) {
  //     throw ValidationException('Starting location and destination cannot be the same');
  //   }

  //   // Check seats available (drivers usually offer 1-8 seats)
  //   if (seatsAvailable < 1 || seatsAvailable > 8) {
  //     throw ValidationException('Available seats must be between 1 and 8');
  //   }

  //   // Check max detour distance
  //   if (maxDetourDistance < 0 || maxDetourDistance > 50) {
  //     throw ValidationException('Max detour distance must be between 0 and 50 km');
  //   }

  //   // Check date/time
  //   final departureDateTime = DateTime(
  //     selectedDate.year,
  //     selectedDate.month,
  //     selectedDate.day,
  //     departureTime.hour,
  //     departureTime.minute,
  //   );

  //   if (departureDateTime.isBefore(DateTime.now())) {
  //     throw ValidationException('Departure time cannot be in the past');
  //   }

  //   // Check if too far in future (optional)
  //   final maxFutureDate = DateTime.now().add(const Duration(days: 365));
  //   if (departureDateTime.isAfter(maxFutureDate)) {
  //     throw ValidationException('Departure time cannot be more than a year in the future');
  //   }

  //   // Business rule: Give at least 30 minutes notice
  //   final minNoticeTime = DateTime.now().add(const Duration(minutes: 30));
  //   if (departureDateTime.isBefore(minNoticeTime)) {
  //     throw ValidationException('Please provide at least 30 minutes notice for ride offers');
  //   }

  //   print('✅ All ride offer validation passed');
  // }

  /// Check if user can edit a ride offer
  // bool canEditRideOffer(RideOffer offer) {
  //   return offer.canBeEdited; // Uses the model's business logic
  // }

  /// Get ride offers departing soon (next 2 hours)
  // Future<List<RideOffer>> getRideOffersDepartingSoon() async {
  //   final allOffers = await getAvailableRideOffers();
  //   final now = DateTime.now();
  //   final twoHoursFromNow = now.add(Duration(hours: 2));
    
  //   return allOffers.where((offer) {
  //     return offer.departureDateTime.isAfter(now) && 
  //            offer.departureDateTime.isBefore(twoHoursFromNow);
  //   }).toList();
  // }

  /// Get ride offers for a specific route
//   Future<List<RideOffer>> getRideOffersForRoute({
//     required String startingLocation,
//     required String destination,
//   }) async {
//     return await searchRideOffers(
//       startingLocation: startingLocation,
//       destination: destination,
//     );
//   }
// }

/// Custom exception for validation errors
// class ValidationException implements Exception {
//   final String message;
  
//   const ValidationException(this.message);
  
//   @override
//   String toString() => 'ValidationException: $message';
}