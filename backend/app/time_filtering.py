# Basic Time Filtering for Ride Matching
# Simple, clean implementation for testing and development

import math
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class BasicTimeFilter:
    """Simple time-based filtering for ride matching"""
    
    def __init__(self):
        # Configuration - easy to adjust for testing
        self.DEFAULT_TIME_FLEXIBILITY_MINUTES = 20
        self.DEFAULT_MAX_DETOUR_MINUTES = 15
        self.COORDINATION_BUFFER_MINUTES = 5
        
    async def filter_drivers_by_time(
        self, 
        ride_request: Dict, 
        potential_drivers: List[Dict]
    ) -> List[Dict]:
        """
        Main function: Filter drivers by time compatibility
        
        Args:
            ride_request: Passenger's ride request
            potential_drivers: List of drivers to check
            
        Returns:
            List of time-compatible drivers with timing details
        """
        
        logger.info(f"Filtering {len(potential_drivers)} drivers for time compatibility")
        
        # Extract passenger requirements
        passenger_desired_time = datetime.fromisoformat(ride_request['desired_pickup_time'])
        passenger_flexibility = ride_request.get('time_flexibility_minutes', self.DEFAULT_TIME_FLEXIBILITY_MINUTES)
        
        compatible_drivers = []
        
        for driver in potential_drivers:
            try:
                # Check if this driver is time-compatible
                is_compatible, timing_details = await self._check_driver_compatibility(
                    driver=driver,
                    passenger_desired_time=passenger_desired_time,
                    passenger_flexibility=passenger_flexibility,
                    passenger_pickup_location=(ride_request['pickup_lat'], ride_request['pickup_lng'])
                )
                
                if is_compatible:
                    # Add timing information to driver data
                    driver_with_timing = driver.copy()
                    driver_with_timing['timing'] = timing_details
                    compatible_drivers.append(driver_with_timing)
                    
                    logger.info(f"✅ Driver {driver['user_id']}: {timing_details['explanation']}")
                else:
                    logger.debug(f"❌ Driver {driver['user_id']}: {timing_details['explanation']}")
                    
            except Exception as e:
                logger.error(f"Error checking driver {driver.get('user_id', 'unknown')}: {e}")
                continue
        
        # Sort by timing quality (best matches first)
        compatible_drivers.sort(key=lambda d: (
            abs(d['timing']['time_difference_minutes']),  # Closer to desired time = better
            d['timing']['travel_time_minutes']            # Less detour = better
        ))
        
        logger.info(f"Found {len(compatible_drivers)} time-compatible drivers")
        return compatible_drivers
    
    async def _check_driver_compatibility(
        self, 
        driver: Dict, 
        passenger_desired_time: datetime,
        passenger_flexibility: int,
        passenger_pickup_location: Tuple[float, float]
    ) -> Tuple[bool, Dict]:
        """
        Check if a driver is time-compatible with passenger
        
        This handles your scenario:
        Driver departs 6:20 PM → travels 10 min → arrives 6:30 PM
        Passenger wants 6:30 PM → Perfect match!
        """
        
        # When does the driver depart?
        driver_departure_time = datetime.fromisoformat(driver['departure_time'])
        driver_max_detour = driver.get('max_pickup_detour_minutes', self.DEFAULT_MAX_DETOUR_MINUTES)
        
        # How long to travel from driver to passenger pickup?
        travel_time_minutes = self._calculate_travel_time(
            from_location=(driver['pickup_lat'], driver['pickup_lng']),
            to_location=passenger_pickup_location
        )
        
        # When will driver actually reach passenger?
        estimated_pickup_time = driver_departure_time + timedelta(minutes=travel_time_minutes)
        
        # How different is this from passenger's desired time?
        time_diff_seconds = (estimated_pickup_time - passenger_desired_time).total_seconds()
        time_difference_minutes = int(time_diff_seconds / 60)
        
        # What's passenger's acceptable time window?
        earliest_acceptable = passenger_desired_time - timedelta(minutes=passenger_flexibility)
        latest_acceptable = passenger_desired_time + timedelta(
            minutes=passenger_flexibility + self.COORDINATION_BUFFER_MINUTES
        )
        
        # Check compatibility constraints
        is_within_passenger_window = earliest_acceptable <= estimated_pickup_time <= latest_acceptable
        is_within_driver_detour_limit = travel_time_minutes <= driver_max_detour
        
        # Final compatibility decision
        is_compatible = is_within_passenger_window and is_within_driver_detour_limit
        
        # Create detailed timing information
        timing_details = {
            'driver_departure_time': driver_departure_time.strftime('%H:%M'),
            'estimated_pickup_time': estimated_pickup_time.strftime('%H:%M'),
            'passenger_desired_time': passenger_desired_time.strftime('%H:%M'),
            'time_difference_minutes': time_difference_minutes,
            'travel_time_minutes': travel_time_minutes,
            'is_compatible': is_compatible,
            'explanation': self._create_explanation(
                driver_departure_time, travel_time_minutes, estimated_pickup_time,
                passenger_desired_time, time_difference_minutes, is_compatible,
                is_within_passenger_window, is_within_driver_detour_limit
            )
        }
        
        return is_compatible, timing_details
    
    def _calculate_travel_time(
        self, 
        from_location: Tuple[float, float], 
        to_location: Tuple[float, float]
    ) -> int:
        """
        Calculate travel time between two locations
        
        For testing: uses simple distance-based estimation
        For production: replace with Google Maps/Mapbox API
        """
        
        # Calculate straight-line distance
        distance_km = self._haversine_distance(
            from_location[0], from_location[1],
            to_location[0], to_location[1]
        )
        
        # Estimate travel time
        # Assume average city speed of 25 km/h
        travel_time_hours = distance_km / 25
        travel_time_minutes = int(travel_time_hours * 60)
        
        # Add buffer for city driving (traffic lights, turns, etc.)
        buffer_minutes = max(2, int(distance_km * 0.5))
        
        # Return minimum 5 minutes (even for very short distances)
        return max(5, travel_time_minutes + buffer_minutes)
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        return 6371 * c
    
    def _create_explanation(
        self, 
        driver_departure: datetime, 
        travel_time: int,
        estimated_pickup: datetime, 
        passenger_desired: datetime,
        time_diff: int, 
        is_compatible: bool,
        within_window: bool, 
        within_detour: bool
    ) -> str:
        """Create human-readable explanation of compatibility"""
        
        departure_str = driver_departure.strftime("%H:%M")
        pickup_str = estimated_pickup.strftime("%H:%M")
        desired_str = passenger_desired.strftime("%H:%M")
        
        base = f"Driver departs {departure_str} → travels {travel_time}min → arrives {pickup_str}. Passenger wants {desired_str}."
        
        if is_compatible:
            if time_diff == 0:
                return f"{base} Perfect timing! ✨"
            elif time_diff > 0:
                return f"{base} Driver {time_diff}min late - acceptable. ✅"
            else:
                return f"{base} Driver {abs(time_diff)}min early - acceptable. ✅"
        else:
            if not within_window:
                if time_diff > 0:
                    return f"{base} Too late ({time_diff}min). ❌"
                else:
                    return f"{base} Too early ({abs(time_diff)}min). ❌"
            if not within_detour:
                return f"{base} Driver detour too long ({travel_time}min). ❌"
        
        return f"{base} Not compatible. ❌"

# Integration with your existing ride matching service
class SimpleRideMatching:
    """Updated ride matching with time filtering"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.time_filter = BasicTimeFilter()
    
    async def find_compatible_drivers(self, ride_request: Dict) -> List[Dict]:
        """Find drivers compatible with time requirements"""
        
        logger.info(f"Finding drivers for request {ride_request['id']}")
        
        # Step 1: Get potential drivers from database (time window pre-filter)
        potential_drivers = await self._get_drivers_in_time_window(ride_request)
        
        if not potential_drivers:
            logger.info("No drivers found in time window")
            return []
        
        # Step 2: Apply detailed time filtering
        time_compatible_drivers = await self.time_filter.filter_drivers_by_time(
            ride_request=ride_request,
            potential_drivers=potential_drivers
        )
        
        # Step 3: Create final match records
        final_matches = self._create_match_records(ride_request, time_compatible_drivers)
        
        return final_matches
    
    async def _get_drivers_in_time_window(self, ride_request: Dict) -> List[Dict]:
        """Get drivers from database within broad time window"""
        
        passenger_time = datetime.fromisoformat(ride_request['desired_pickup_time'])
        
        # Broad time window: ±2 hours
        window_start = passenger_time - timedelta(hours=2)
        window_end = passenger_time + timedelta(hours=2)
        
        logger.info(f"Querying drivers between {window_start.strftime('%H:%M')} and {window_end.strftime('%H:%M')}")
        
        result = self.supabase.table('ride_offers')\
            .select('*')\
            .eq('status', 'active')\
            .gte('departure_time', window_start.isoformat())\
            .lte('departure_time', window_end.isoformat())\
            .gt('available_seats', 0)\
            .order('departure_time')\
            .execute()
        
        drivers = result.data
        logger.info(f"Found {len(drivers)} drivers in time window")
        
        return drivers
    
    def _create_match_records(self, ride_request: Dict, compatible_drivers: List[Dict]) -> List[Dict]:
        """Create final match records for database storage"""
        
        matches = []
        
        for driver in compatible_drivers:
            timing = driver['timing']
            
            match_record = {
                'ride_request_id': ride_request['id'],
                'ride_offer_id': driver['id'],
                'driver_id': driver['user_id'],
                'passenger_id': ride_request['user_id'],
                'estimated_pickup_time': timing['estimated_pickup_time'],
                'time_difference_minutes': timing['time_difference_minutes'],
                'travel_time_minutes': timing['travel_time_minutes'],
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'explanation': timing['explanation']
            }
            
            matches.append(match_record)
        
        return matches

# Simple test function for your scenario
async def test_your_scenario():
    """Test the exact scenario you described"""
    
    print("🧪 Testing your scenario...")
    
    # Mock driver (departs 6:20 PM)
    test_driver = {
        'id': 'driver_123',
        'user_id': 'user_456',
        'departure_time': '2025-07-08T18:20:00',  # 6:20 PM
        'pickup_lat': 37.7749,  # San Francisco
        'pickup_lng': -122.4194,
        'max_pickup_detour_minutes': 15,
        'available_seats': 3
    }
    
    # Mock passenger request (wants 6:30 PM pickup)
    test_request = {
        'id': 'request_789',
        'user_id': 'user_101',
        'pickup_lat': 37.7799,  # About 10 minutes away from driver
        'pickup_lng': -122.4144,
        'desired_pickup_time': '2025-07-08T18:30:00',  # 6:30 PM
        'time_flexibility_minutes': 15
    }
    
    # Run the time filtering
    time_filter = BasicTimeFilter()
    compatible_drivers = await time_filter.filter_drivers_by_time(
        ride_request=test_request,
        potential_drivers=[test_driver]
    )
    
    # Show results
    if compatible_drivers:
        driver = compatible_drivers[0]
        timing = driver['timing']
        
        print("\n🎯 TEST RESULTS:")
        print(f"Driver departs: {timing['driver_departure_time']}")
        print(f"Travel time: {timing['travel_time_minutes']} minutes")
        print(f"Driver arrives: {timing['estimated_pickup_time']}")
        print(f"Passenger wants: {timing['passenger_desired_time']}")
        print(f"Time difference: {timing['time_difference_minutes']} minutes")
        print(f"Compatible: {timing['is_compatible']}")
        print(f"Explanation: {timing['explanation']}")
        
        # Expected: Driver departs 18:20 + 10min travel = arrives 18:30 = perfect match!
    else:
        print("❌ No compatible drivers found")

# How to use in your existing code
async def integrate_with_existing_matching(ride_request: Dict, supabase_client):
    """Integration function for your existing ride matching service"""
    
    # Create matching service with time filtering
    matching_service = SimpleRideMatching(supabase_client)
    
    # Find compatible drivers
    compatible_drivers = await matching_service.find_compatible_drivers(ride_request)
    
    # Store matches in database
    if compatible_drivers:
        result = supabase_client.table('ride_matches').insert(compatible_drivers).execute()
        logger.info(f"Stored {len(compatible_drivers)} matches in database")
    
    return compatible_drivers

if __name__ == "__main__":
    import asyncio
    
    # Run the test
    asyncio.run(test_your_scenario())