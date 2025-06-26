/**
 * Related files: repositories/ride_repository.dart
 * services/ride_service.dart
 * model/ride_request_model.dart
 * 
 * CRUD operations
 */

import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/ride_request_model.dart';

class RideRepository {
  final SupabaseClient _client = Supabase.instance.client;

  /// Get all ride requests (for testing/viewing)
  Future<List<RideRequest>> getAllRideRequests() async {
    try {
      print('📋 Fetching all ride requests...');
      
      final response = await _client
          .from('ride_requests')
          .select()
          .order('created_at', ascending: false);

      print('✅ Found ${response.length} ride requests');
      return response.map<RideRequest>((json) => RideRequest.fromJson(json)).toList();
      
    } on PostgrestException catch (e) {
      print('❌ Database error: ${e.message}');
      throw Exception('Database error: ${e.message}');
    } catch (e) {
      print('❌ Unexpected error: $e');
      throw Exception('Failed to fetch ride requests: $e');
    }
  }

  /// Test database connection
  Future<bool> testConnection() async {
    try {
      print('🔍 Testing database connection...');
      await _client.from('ride_requests').select().limit(1);
      print('✅ Database connection successful');
      return true;
    } catch (e) {
      print('❌ Database connection failed: $e');
      return false;
    }
  }

  // insert to db
Future<RideRequest> createRideRequest(RideRequest request) async {
  try {
    print('🚀 Inserting ride request to database...');
    
    final jsonData = request.toJson();
    print('📤 EXACT JSON being sent:');
    jsonData.forEach((key, value) {
      print('   $key: $value (${value.runtimeType})');
    });
    
    final response = await _client
        .from('Ride_Request')
        .insert(jsonData)
        .select()
        .single();

    print('✅ Successfully inserted: ${response['id']}');
    return RideRequest.fromJson(response);
    
  } catch (e) {
    print('❌ Insert failed: $e');
    throw e;
  }
}
}