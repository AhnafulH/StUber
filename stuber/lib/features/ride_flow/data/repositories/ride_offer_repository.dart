/**
 * Related files: repositories/ride_repository.dart
 * services/ride_service.dart
 * model/ride_request_model.dart
 * 
 * CRUD operations
 */

import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/ride_offer_model.dart';

class RideOfferRepository {
  final SupabaseClient _client = Supabase.instance.client;

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
Future<RideOfferModel> createRideOffer(RideOfferModel request) async {
  try {
    print('🚀 Inserting ride request to database...');
    
    final jsonData = request.toJson();
    print('📤 EXACT JSON being sent:');
    jsonData.forEach((key, value) {
      print('   $key: $value (${value.runtimeType})');
    });
    
    final response = await _client
        .from('Ride_Offer')
        .insert(jsonData)
        .select()
        .single();

    print('✅ Successfully inserted: ${response['id']}');
    return RideOfferModel.fromJson(response);
    
  } catch (e) {
    print('❌ Insert failed: $e');
    throw e;
  }
}
}