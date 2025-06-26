/**
 * Related files: repositories/ride_repository.dart
 * services/ride_service.dart
 * model/ride_request_model.dart
 * 
 * 
 * 
 *  Business rules - What's allowed and what's not?
 *  Validation - Is the data valid for your app's rules?
 *  Coordination - Orchestrates multiple operations
 * User-friendly interface - Provides easy methods for UI to use
 */


import 'package:flutter/material.dart';
import '../models/ride_request_model.dart';
import '../repositories/ride_repository.dart';

class RideService {
  final RideRepository _repository = RideRepository();

  /// Create ride request from your form data
  Future<RideRequest> createRideRequestFromForm({
    required String startingLocation,
    required String destination,
    required int seatsNeeded,  // Changed from seatsNeeded to passengers
    required DateTime selectedDate,
    required TimeOfDay departureTime,
    double? startingLatitude,
    double? startingLongitude,
    double? destinationLatitude,
    double? destinationLongitude,
  }) async {
    
    print('🎯 RideService: Creating ride request...');
    
    // 1. Basic validation
    _validateInput(
      startingLocation: startingLocation,
      destination: destination,
      seatsNeeded: seatsNeeded,
      selectedDate: selectedDate,
      departureTime: departureTime,
    );

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
    final request = RideRequest(
      startingLocation: startingLocation.trim(),
      startingLatitude: startingLatitude,
      startingLongitude: startingLongitude,
      destination: destination.trim(),
      destinationLatitude: destinationLatitude,
      destinationLongitude: destinationLongitude,
      seatsNeeded: seatsNeeded,  // Changed from seatsNeeded
      departureDateTime: departureDateTime,
    );

    print('🚗 Created ride request: $request');

    // 4. Save to database
    return await _repository.createRideRequest(request);
  }

  /// Get all ride requests (for testing)
  Future<List<RideRequest>> getAllRideRequests() async {
    return await _repository.getAllRideRequests();
  }

  /// Test if database is working
  Future<bool> testDatabaseConnection() async {
    return await _repository.testConnection();
  }

  /// Validate form input
  void _validateInput({
    required String startingLocation,
    required String destination,
    required int seatsNeeded,  // Changed from seatsNeeded to passengers
    required DateTime selectedDate,
    required TimeOfDay departureTime,
  }) {
    // Check starting location
    if (startingLocation.trim().isEmpty) {
      throw ValidationException('Starting location cannot be empty');
    }

    // Check destination
    if (destination.trim().isEmpty) {
      throw ValidationException('Destination cannot be empty');
    }

    // Check if they're the same
    if (startingLocation.trim().toLowerCase() == destination.trim().toLowerCase()) {
      throw ValidationException('Starting location and destination cannot be the same');
    }

    // Check passengers (changed from seats)
    if (seatsNeeded < 1 || seatsNeeded > 8) {
      throw ValidationException('Passengers must be between 1 and 8');
    }

    // Check date/time
    final departureDateTime = DateTime(
      selectedDate.year,
      selectedDate.month,
      selectedDate.day,
      departureTime.hour,
      departureTime.minute,
    );

    if (departureDateTime.isBefore(DateTime.now())) {
      throw ValidationException('Departure time cannot be in the past');
    }

    // Check if too far in future (optional)
    final maxFutureDate = DateTime.now().add(const Duration(days: 365));
    if (departureDateTime.isAfter(maxFutureDate)) {
      throw ValidationException('Departure time cannot be more than a year in the future');
    }

    print('✅ All validation passed');
  }
}

/// Custom exception for validation errors
class ValidationException implements Exception {
  final String message;
  
  const ValidationException(this.message);
  
  @override
  String toString() => 'ValidationException: $message';
}