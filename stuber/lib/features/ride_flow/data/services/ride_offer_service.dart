import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:supabase_flutter/supabase_flutter.dart';
import 'dart:convert';
import '../models/ride_offer_model.dart';

class RideOfferService {
  // Replace with your actual FastAPI server URL
  static const String baseUrl = 'http://10.21.71.179:8000'; // Update this!
  
  static const Map<String, String> headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  /// Create ride offer from your form data - Updated to use FastAPI
  Future<RideOfferResponse> createRideOfferFromForm({
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

    final supabase = Supabase.instance.client;
    final currentSession = supabase.auth.currentSession;

    if (currentSession == null) {
      throw Exception("User must be logged in to create Ride Offer");
    }

    final uuid = currentSession.user.id;

    // 1. Input validation (you can uncomment your validation if needed)
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
    final rideOfferCreate = RideOfferCreate(
      uuid: uuid,
      startingLocation: startingLocation.trim(),
      destination: destination.trim(),
      seatsAvailable: seatsAvailable,
      startingLatitude: startingLatitude,
      startingLongitude: startingLongitude,
      destinationLatitude: destinationLatitude,
      destinationLongitude: destinationLongitude,
      departureDateTime: departureDateTime,
      maxDetourDistance: maxDetourDistance.toDouble(),
    );

    print('🚗 Sending ride offer to API: ${rideOfferCreate.toJson()}');

    // 4. Send to FastAPI instead of local database
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/ride-offers'),
        headers: headers,
        body: json.encode(rideOfferCreate.toJson()),
      );

      print('📡 API Response Status: ${response.statusCode}');
      print('📡 API Response Body: ${response.body}');

      if (response.statusCode == 200) {
        final responseData = json.decode(response.body);
        final createdOffer = RideOfferResponse.fromJson(responseData);
        
        print('✅ Ride offer created successfully! ID: ${createdOffer.id}');
        return createdOffer;
      } else {
        // Handle HTTP errors
        final errorBody = response.body;
        print('❌ API Error: ${response.statusCode} - $errorBody');
        throw Exception('Failed to create ride offer: ${response.statusCode} - $errorBody');
      }
    } catch (e) {
      print('❌ Network Error: $e');
      if (e is http.ClientException) {
        throw Exception('Network error: Unable to connect to server. Please check your internet connection.');
      } else {
        throw Exception('Error creating ride offer: $e');
      }
    }
  }
}