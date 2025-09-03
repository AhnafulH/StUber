import 'package:flutter/material.dart';
import '../models/ride_request_model.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class RideService {
  // Replace with your actual FastAPI server URL
  static const String baseUrl = 'http://localhost:8000'; // Update this!
  
  static const Map<String, String> headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  /// Create ride request from your form data - Updated to use FastAPI
  Future<RideRequestResponse> createRideRequestFromForm({
    required String startingLocation,
    required String destination,
    required int seatsNeeded,
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

    // Additional validation for coordinates (required by FastAPI)
    if (startingLatitude == null || startingLongitude == null ||
        destinationLatitude == null || destinationLongitude == null) {
      throw Exception('Location coordinates are required');
    }

    // 2. Combine date and time
    final departureDateTime = DateTime(
      selectedDate.year,
      selectedDate.month,
      selectedDate.day,
      departureTime.hour,
      departureTime.minute,
    );
    print('📅 Departure: $departureDateTime');

    // 3. Create the API request object
    final rideRequestCreate = RideRequestCreate(
      startingLocation: startingLocation.trim(),
      destination: destination.trim(),
      seatsNeeded: seatsNeeded,
      startingLatitude: startingLatitude,
      startingLongitude: startingLongitude,
      destinationLatitude: destinationLatitude,
      destinationLongitude: destinationLongitude,
      departureDateTime: departureDateTime,
    );

    print('🚗 Sending ride request to API: ${rideRequestCreate.toJson()}');

    // 4. Send to FastAPI instead of local database
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/ride-requests'),
        headers: headers,
        body: json.encode(rideRequestCreate.toJson()),
      );

      print('📡 API Response Status: ${response.statusCode}');
      print('📡 API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = json.decode(response.body);
        final createdRequest = RideRequestResponse.fromJson(responseData);
        
        print('✅ Ride request created successfully! ID: ${createdRequest.id}');
        return createdRequest;
      } else {
        // Handle HTTP errors
        final errorBody = response.body;
        print('❌ API Error: ${response.statusCode} - $errorBody');
        throw Exception('Failed to create ride request: ${response.statusCode} - $errorBody');
      }
    } catch (e) {
      print('❌ Network Error: $e');
      if (e is http.ClientException) {
        throw Exception('Network error: Unable to connect to server. Please check your internet connection.');
      } else {
        throw Exception('Error creating ride request: $e');
      }
    }
  }

  // Keep your existing validation method
  void _validateInput({
    required String startingLocation,
    required String destination,
    required int seatsNeeded,
    required DateTime selectedDate,
    required TimeOfDay departureTime,
  }) {
    if (startingLocation.trim().isEmpty) {
      throw Exception('Starting location cannot be empty');
    }
    
    if (destination.trim().isEmpty) {
      throw Exception('Destination cannot be empty');
    }
    
    if (seatsNeeded < 1 || seatsNeeded > 8) {
      throw Exception('Seats needed must be between 1 and 8');
    }
    
    final departureDateTime = DateTime(
      selectedDate.year,
      selectedDate.month,
      selectedDate.day,
      departureTime.hour,
      departureTime.minute,
    );
    
    if (departureDateTime.isBefore(DateTime.now())) {
      throw Exception('Departure time cannot be in the past');
    }
  }

  // Optional: Method to convert your existing RideRequest model to RideRequestCreate
  // if you want to keep using your existing model elsewhere
  RideRequestCreate convertToApiModel(dynamic rideRequestModel) {
    return RideRequestCreate(
      startingLocation: rideRequestModel.startingLocation,
      destination: rideRequestModel.destination,
      seatsNeeded: rideRequestModel.seatsNeeded,
      startingLatitude: rideRequestModel.startingLatitude ?? 0.0,
      startingLongitude: rideRequestModel.startingLongitude ?? 0.0,
      destinationLatitude: rideRequestModel.destinationLatitude ?? 0.0,
      destinationLongitude: rideRequestModel.destinationLongitude ?? 0.0,
      departureDateTime: rideRequestModel.departureDateTime,
    );
  }

  // Additional API methods you might need:

  // Get all ride requests
  Future<List<RideRequestResponse>> getAllRideRequests() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/ride-requests'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = json.decode(response.body);
        return jsonList.map((json) => RideRequestResponse.fromJson(json)).toList();
      } else {
        throw Exception('Failed to fetch ride requests: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Get specific ride request
  Future<RideRequestResponse> getRideRequest(int requestId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/ride-requests/$requestId'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return RideRequestResponse.fromJson(json.decode(response.body));
      } else if (response.statusCode == 404) {
        throw Exception('Ride request not found');
      } else {
        throw Exception('Failed to fetch ride request: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Test API connection
  Future<bool> testConnection() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: headers,
      );
      return response.statusCode == 200;
    } catch (e) {
      print('❌ Connection test failed: $e');
      return false;
    }
  }
}

class ValidationException implements Exception {
  final String message;
  
  const ValidationException(this.message);
  
  @override
  String toString() => 'ValidationException: $message';
}