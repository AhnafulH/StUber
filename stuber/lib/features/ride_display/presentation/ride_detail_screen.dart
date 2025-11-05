import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:stuber/features/ride_display/presentation/ride_model.dart';
import 'package:stuber/features/ride_display/data/unified_ride_repository.dart';

class RideDetailScreen extends StatefulWidget {
  final RideItem rideItem;

  const RideDetailScreen({
    Key? key,
    required this.rideItem,
  }) : super(key: key);

  @override
  State<RideDetailScreen> createState() => _RideDetailScreenState();
}

class _RideDetailScreenState extends State<RideDetailScreen> {
  final UnifiedRideRepository _repository = UnifiedRideRepository();
  late RideItem currentRide;
  bool _isLoading = false;
  List<RideMatch> _rideMatches = [];
  bool _isLoadingMatches = false;
  RideConfirmed? _confirmedRide;

  @override
  void initState() {
    super.initState();
    currentRide = widget.rideItem;
    _loadRideMatches();
    _checkConfirmedRide(); 
  }

  bool get isMyRide => currentRide.userUuid == 
      Supabase.instance.client.auth.currentUser?.id;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Icon(
              currentRide.rideType == RideType.request ? Icons.search : Icons.local_offer,
              color: Colors.white,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text('${_getRideTypeLabel()} #${currentRide.id}'),
          ],
        ),
        backgroundColor: _getRideTypeColor(),
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (isMyRide) ...[
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: _handleEdit,
            ),
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: _handleDelete,
            ),
          ] else ...[
            IconButton(
              icon: const Icon(Icons.message),
              onPressed: _handleContact,
            ),
          ],
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header card with ride type
                  Container(
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: _getRideTypeColor(),
                      borderRadius: const BorderRadius.only(
                        bottomLeft: Radius.circular(24),
                        bottomRight: Radius.circular(24),
                      ),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  currentRide.rideType == RideType.request 
                                      ? Icons.search 
                                      : Icons.local_offer,
                                  color: Colors.white,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  _getRideTypeLabel().toUpperCase(),
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 14,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            currentRide.departureDatetime != null
                                ? DateFormat('EEEE, MMM dd, yyyy').format(currentRide.departureDatetime!)
                                : 'Date not set',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            currentRide.departureDatetime != null
                                ? DateFormat('hh:mm a').format(currentRide.departureDatetime!)
                                : 'Time not set',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Route information
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Card(
                      elevation: 2,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Route Details',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 16),
                            _RoutePoint(
                              icon: Icons.radio_button_checked,
                              iconColor: Colors.green,
                              label: 'Pickup',
                              location: currentRide.startLocation,
                              coordinates: _getStartCoordinates(),
                            ),
                            const SizedBox(height: 16),
                            _RoutePoint(
                              icon: Icons.location_on,
                              iconColor: Colors.red,
                              label: 'Destination',
                              location: currentRide.endDestination,
                              coordinates: _getDestinationCoordinates(),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Ride details
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Card(
                      elevation: 2,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${_getRideTypeLabel()} Details',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 16),
                            _DetailRow(
                              icon: currentRide.rideType == RideType.request 
                                  ? Icons.person_add 
                                  : Icons.airline_seat_recline_normal,
                              label: currentRide.rideType == RideType.request 
                                  ? 'Seats Needed' 
                                  : 'Seats Available',
                              value: _getSeatsValue(),
                            ),
                            const SizedBox(height: 12),
                            _DetailRow(
                              icon: Icons.schedule,
                              label: 'Created',
                              value: currentRide.createdAt != null
                                  ? DateFormat('MMM dd, yyyy hh:mm a').format(currentRide.createdAt!)
                                  : 'Unknown',
                            ),
                            
                            // Offer-specific details
                            if (currentRide is RideOffer) ...[
                              const SizedBox(height: 12),
                              _buildOfferSpecificDetails(),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ),

                  // User information
                  if (currentRide.profile != null) ...[
                    const SizedBox(height: 16),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      child: Card(
                        elevation: 2,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'User Information',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 16),
                              Row(
                                children: [
                                  CircleAvatar(
                                    radius: 30,
                                    backgroundColor: _getRideTypeColor().withOpacity(0.2),
                                    child: Text(
                                      currentRide.profile!.fullName?.isNotEmpty == true
                                          ? currentRide.profile!.fullName![0].toUpperCase()
                                          : '?',
                                      style: TextStyle(
                                        fontSize: 24,
                                        fontWeight: FontWeight.bold,
                                        color: _getRideTypeColor(),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          currentRide.profile!.fullName ?? 'Unknown User',
                                          style: const TextStyle(
                                            fontSize: 18,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Container(
                                          padding: const EdgeInsets.symmetric(
                                            horizontal: 8,
                                            vertical: 4,
                                          ),
                                          decoration: BoxDecoration(
                                            color: _getUserTypeColor(currentRide.profile!.userType),
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                          child: Text(
                                            currentRide.profile!.userType.toUpperCase(),
                                            style: const TextStyle(
                                              fontSize: 12,
                                              color: Colors.white,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ),
                                        if (currentRide.profile!.phone != null) ...[
                                          const SizedBox(height: 8),
                                          Row(
                                            children: [
                                              Icon(
                                                Icons.phone,
                                                size: 16,
                                                color: Colors.grey.shade600,
                                              ),
                                              const SizedBox(width: 4),
                                              Text(
                                                currentRide.profile!.phone!,
                                                style: TextStyle(
                                                  fontSize: 14,
                                                  color: Colors.grey.shade600,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ],
                                        if (currentRide.profile!.email != null) ...[
                                          const SizedBox(height: 4),
                                          Row(
                                            children: [
                                              Icon(
                                                Icons.email,
                                                size: 16,
                                                color: Colors.grey.shade600,
                                              ),
                                              const SizedBox(width: 4),
                                              Text(
                                                currentRide.profile!.email!,
                                                style: TextStyle(
                                                  fontSize: 14,
                                                  color: Colors.grey.shade600,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ],
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],

                  // Ride Matches section
                  const SizedBox(height: 16),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Card(
                      elevation: 2,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  currentRide.rideType == RideType.request 
                                      ? Icons.local_offer 
                                      : Icons.search,
                                  color: _getRideTypeColor(),
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  currentRide.rideType == RideType.request 
                                      ? 'Matching Offers' 
                                      : 'Matching Requests',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const Spacer(),
                                if (_isLoadingMatches)
                                  const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  ),
                              ],
                            ),
                            const SizedBox(height: 16),
                            _buildRideMatchesList(),
                          ],
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 100), // Space for FAB
                ],
              ),
            ),
      
      // Floating action button with main action
      floatingActionButton: !isMyRide && currentRide.rideType == RideType.offer
          ? FloatingActionButton.extended(
              onPressed: _handleBookRide,
              backgroundColor: Colors.green,
              icon: const Icon(Icons.book_online),
              label: const Text('Book This Ride'),
            )
          : null,
    );
  }

  Widget _buildRideMatchesList() {
    if (_isLoadingMatches) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(20),
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (_rideMatches.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.grey.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Column(
          children: [
            Icon(
              currentRide.rideType == RideType.request 
                  ? Icons.local_offer_outlined 
                  : Icons.search_off,
              size: 48,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 12),
            Text(
              currentRide.rideType == RideType.request 
                  ? 'No matching offers found yet' 
                  : 'No matching requests found yet',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Check back later or adjust your ride details',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade500,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        // Matches count
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: _getRideTypeColor().withOpacity(0.1),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            '${_rideMatches.length} match${_rideMatches.length == 1 ? '' : 'es'} found',
            style: TextStyle(
              color: _getRideTypeColor(),
              fontWeight: FontWeight.w600,
              fontSize: 12,
            ),
          ),
        ),
        const SizedBox(height: 16),
        
        // Matches list
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _rideMatches.length,
          separatorBuilder: (context, index) => const SizedBox(height: 12),
          itemBuilder: (context, index) {
            final match = _rideMatches[index];
            return _RideMatchCard(
              match: match,
              currentRideType: currentRide.rideType,
              isMyRide: isMyRide,
              onTap: () => _handleMatchTap(match),
              onDriverAction: isMyRide && currentRide.rideType == RideType.offer
                ? _handleDriverAction
                : null,
              onRiderAction: isMyRide && currentRide.rideType == RideType.request
                ? _handleRiderAction
                : null,
            );
          },
        ),
      ],
    );
  }

  void _handleMatchTap(RideMatch match) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _RideMatchBottomSheet(match: match),
    );
  }

  Future<void> _loadRideMatches() async {
    setState(() {
      _isLoadingMatches = true;
    });

    try {
      List<RideMatch> matches = [];
      
      if (isMyRide) {
        // If it's MY ride, show different matches based on ride type
        if (currentRide.rideType == RideType.offer) {
          // PHASE 2: I'm a driver - show riders waiting for my decision
          matches = await _repository.getPendingDriverMatches(currentRide.id);
        } else {
          // PHASE 3: I'm a rider - show drivers who accepted me
          matches = await _repository.getDriversWhoAccepted(currentRide.id);
        }
      } else {
        // If it's NOT my ride, show all matches (read-only view)
        matches = await _repository.getRideMatches(
          currentRide.id, 
          currentRide.rideType
        );
      }
      
      setState(() {
        _rideMatches = matches;
        _isLoadingMatches = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingMatches = false;
      });
      print('Error loading ride matches: $e');
    }
  }

  Widget _buildOfferSpecificDetails() {
    final offer = currentRide as RideOffer;
    return Column(
      children: [
        if (offer.maxDetourDistance != null) ...[
          _DetailRow(
            icon: Icons.route,
            label: 'Max Detour',
            value: '${offer.maxDetourDistance!.toStringAsFixed(1)} km',
          ),
          const SizedBox(height: 12),
        ],
      ],
    );
  }

  String _getRideTypeLabel() {
    return currentRide.rideType == RideType.request ? 'Request' : 'Offer';
  }

  Color _getRideTypeColor() {
    return currentRide.rideType == RideType.request ? Colors.orange : Colors.green;
  }

  String _getSeatsValue() {
    if (currentRide is RideRequest) {
      return '${(currentRide as RideRequest).numberOfSeats}';
    } else if (currentRide is RideOffer) {
      return '${(currentRide as RideOffer).numberOfSeats}';
    }
    return '1';
  }

  String? _getStartCoordinates() {
    if (currentRide is RideRequest) {
      final request = currentRide as RideRequest;
      if (request.startingLatitude != null && request.startingLongitude != null) {
        return '${request.startingLatitude!.toStringAsFixed(6)}, ${request.startingLongitude!.toStringAsFixed(6)}';
      }
    } else if (currentRide is RideOffer) {
      final offer = currentRide as RideOffer;
      if (offer.startingLatitude != null && offer.startingLongitude != null) {
        return '${offer.startingLatitude!.toStringAsFixed(6)}, ${offer.startingLongitude!.toStringAsFixed(6)}';
      }
    }
    return null;
  }

  String? _getDestinationCoordinates() {
    if (currentRide is RideRequest) {
      final request = currentRide as RideRequest;
      if (request.destinationLatitude != null && request.destinationLongitude != null) {
        return '${request.destinationLatitude!.toStringAsFixed(6)}, ${request.destinationLongitude!.toStringAsFixed(6)}';
      }
    } else if (currentRide is RideOffer) {
      final offer = currentRide as RideOffer;
      if (offer.destinationLatitude != null && offer.destinationLongitude != null) {
        return '${offer.destinationLatitude!.toStringAsFixed(6)}, ${offer.destinationLongitude!.toStringAsFixed(6)}';
      }
    }
    return null;
  }

  Color _getUserTypeColor(String userType) {
    switch (userType.toLowerCase()) {
      case 'rider':
        return Colors.blue;
      case 'driver':
        return Colors.green;
      case 'admin':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  void _handleEdit() {
    // Navigate to edit screen
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Edit ${_getRideTypeLabel().toLowerCase()} functionality will be implemented'),
        backgroundColor: Colors.blue,
      ),
    );
  }

  void _handleContact() {
    if (currentRide.profile?.phone != null) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Contact User'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Name: ${currentRide.profile!.fullName ?? "Unknown"}'),
              if (currentRide.profile!.phone != null)
                Text('Phone: ${currentRide.profile!.phone}'),
              if (currentRide.profile!.email != null)
                Text('Email: ${currentRide.profile!.email}'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
            if (currentRide.profile!.phone != null)
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  // Implement call functionality
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Call functionality would open here')),
                  );
                },
                child: const Text('Call'),
              ),
          ],
        ),
      );
    }
  }

  void _handleBookRide() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Book This Ride'),
        content: const Text('Are you sure you want to book this ride offer?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Booking functionality will be implemented'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            child: const Text('Book'),
          ),
        ],
      ),
    );
  }

  Future<void> _handleDelete() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Delete ${_getRideTypeLabel()}'),
        content: Text('Are you sure you want to delete this ${_getRideTypeLabel().toLowerCase()}? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      setState(() {
        _isLoading = true;
      });

      try {
        await _repository.deleteRide(currentRide);
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('${_getRideTypeLabel()} deleted successfully'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.pop(context, true); // Return true to indicate deletion
        }
      } catch (e) {
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
          
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to delete: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }






    // Handler for driver actions (Phase 2)
  Future<void> _handleDriverAction(int matchId, bool accept) async {
    try {
      if (accept) {
        await _repository.driverAcceptMatch(matchId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Match accepted! Rider will be notified.'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        await _repository.driverRejectMatch(matchId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Match declined.'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
      
      // Reload matches
      _loadRideMatches();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  // Handler for rider actions (Phase 3)
  Future<void> _handleRiderAction(int matchId, bool accept) async {
    try {
      if (accept) {
        // Check if rider already has a confirmed ride
        final hasConfirmed = await _repository.riderHasConfirmedRide(currentRide.id);
        
        if (hasConfirmed) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('You already have a confirmed ride!'),
                backgroundColor: Colors.orange,
              ),
            );
          }
          return;
        }
        
        // Show confirmation dialog before accepting
        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Confirm Ride'),
            content: const Text(
              'Are you sure you want to accept this driver? '
              'This will automatically decline all other pending matches.',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                child: const Text('Confirm'),
              ),
            ],
          ),
        );
        
        if (confirmed == true) {
          await _repository.riderAcceptMatch(matchId, currentRide.id);
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Ride confirmed! Driver will be notified.'),
                backgroundColor: Colors.green,
                duration: Duration(seconds: 3),
              ),
            );
          }
        }
      } else {
        await _repository.riderRejectMatch(matchId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Match declined.'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
      
      // Reload matches
      _loadRideMatches();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _checkConfirmedRide() async {
    try {
      final confirmed = await _repository.getConfirmedMatch(
        currentRide.id,
        currentRide.rideType,
      );
      
      if (confirmed != null) {
        final confirmedRide = await _repository.getConfirmedRideByMatchId(confirmed.id);
        if (mounted) {
          setState(() {
            _confirmedRide = confirmedRide;
          });
        }
      }
    } catch (e) {
      print('Error checking confirmed ride: $e');
    }
  }
}

class _RoutePoint extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String label;
  final String location;
  final String? coordinates;

  const _RoutePoint({
    required this.icon,
    required this.iconColor,
    required this.label,
    required this.location,
    this.coordinates,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: iconColor.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(
            icon,
            color: iconColor,
            size: 20,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                location,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              if (coordinates != null) ...[
                const SizedBox(height: 4),
                Text(
                  coordinates!,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade500,
                    fontFamily: 'monospace',
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _DetailRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.grey.shade100,
            shape: BoxShape.circle,
          ),
          child: Icon(
            icon,
            color: Colors.grey.shade600,
            size: 20,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                  fontWeight: FontWeight.w500,
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
      ],
    );
  }
}

// Match card widget
class _RideMatchCard extends StatelessWidget {
  final RideMatch match;
  final RideType currentRideType;
  final VoidCallback onTap;
  final bool isMyRide;
  final Function(int matchId, bool accept)? onDriverAction;
  final Function(int matchId, bool accept)? onRiderAction;

  const _RideMatchCard({
    required this.match,
    required this.currentRideType,
    required this.onTap,
    required this.isMyRide,
    this.onDriverAction,
    this.onRiderAction,
  });

  @override
  Widget build(BuildContext context) {
    final matchColor = currentRideType == RideType.request ? Colors.green : Colors.orange;
    
    // Get the matched ride based on current ride type
    RideItem? matchedRide;
    if (currentRideType == RideType.request && match.rideOffer != null) {
      matchedRide = match.rideOffer!;
    } else if (currentRideType == RideType.offer && match.rideRequest != null) {
      matchedRide = match.rideRequest!;
    }

    if (matchedRide == null) {
      return const SizedBox.shrink();
    }
    
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: match.isBothAccepted ? Colors.green : Colors.grey.shade200,
            width: match.isBothAccepted ? 2 : 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with match type and status
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: matchColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        currentRideType == RideType.request 
                            ? Icons.local_offer 
                            : Icons.search,
                        size: 16,
                        color: matchColor,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        currentRideType == RideType.request ? 'OFFER' : 'REQUEST',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: matchColor,
                        ),
                      ),
                    ],
                  ),
                ),
                const Spacer(),
                // Match status badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getStatusColor(match.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    match.status.toUpperCase(),
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: _getStatusColor(match.status),
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // User info
            if (matchedRide.profile != null)
              Row(
                children: [
                  CircleAvatar(
                    radius: 20,
                    backgroundColor: matchColor.withOpacity(0.2),
                    child: Text(
                      matchedRide.profile!.fullName?.isNotEmpty == true
                          ? matchedRide.profile!.fullName![0].toUpperCase()
                          : '?',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: matchColor,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          matchedRide.profile!.fullName ?? 'Unknown User',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          matchedRide.profile!.userType.toUpperCase(),
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade600,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            
            const SizedBox(height: 12),
            
            // Route info
            Row(
              children: [
                Icon(Icons.route, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${matchedRide.startLocation} → ${matchedRide.endDestination}',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade700,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 8),
            
            // Additional details
            Row(
              children: [
                if (matchedRide.departureDatetime != null) ...[
                  Icon(Icons.schedule, size: 16, color: Colors.grey.shade600),
                  const SizedBox(width: 4),
                  Text(
                    DateFormat('MMM dd, hh:mm a').format(matchedRide.departureDatetime!),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(width: 16),
                ],
                Icon(Icons.airline_seat_recline_normal, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    _getMatchSeats(matchedRide),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ),
              ],
            ),
            
            // Price if available
            if (match.price != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.attach_money, size: 16, color: Colors.green.shade600),
                  const SizedBox(width: 4),
                  Text(
                    '\$${match.price!.toStringAsFixed(2)}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.green.shade700,
                    ),
                  ),
                ],
              ),
            ],
            
            // Action buttons - only show if it's my ride and not confirmed
            if (isMyRide && !match.isBothAccepted) ...[
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        if (currentRideType == RideType.offer && onDriverAction != null) {
                          onDriverAction!(match.id, false); // Driver rejects
                        } else if (currentRideType == RideType.request && onRiderAction != null) {
                          onRiderAction!(match.id, false); // Rider rejects
                        }
                      },
                      icon: const Icon(Icons.close, size: 18),
                      label: const Text('Decline'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red.shade50,
                        foregroundColor: Colors.red,
                        elevation: 0,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        if (currentRideType == RideType.offer && onDriverAction != null) {
                          onDriverAction!(match.id, true); // Driver accepts
                        } else if (currentRideType == RideType.request && onRiderAction != null) {
                          onRiderAction!(match.id, true); // Rider accepts
                        }
                      },
                      icon: const Icon(Icons.check, size: 18),
                      label: const Text('Accept'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                        elevation: 0,
                      ),
                    ),
                  ),
                ],
              ),
            ],
            
            // Show confirmed badge
            if (match.isBothAccepted) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.check_circle, color: Colors.green.shade700, size: 18),
                    const SizedBox(width: 8),
                    Text(
                      'Ride Confirmed!',
                      style: TextStyle(
                        color: Colors.green.shade700,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return Colors.green;
      case 'pending':
        return Colors.orange;
      case 'waiting for rider':
      case 'waiting for driver':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  String _getMatchSeats(RideItem ride) {
    if (ride is RideRequest) {
      return '${ride.numberOfSeats} seats needed';
    } else if (ride is RideOffer) {
      return '${ride.numberOfSeats} seats available';
    }
    return '1 seat';
  }
}

// Bottom sheet for match details
class _RideMatchBottomSheet extends StatelessWidget {
  final RideMatch match;

  const _RideMatchBottomSheet({required this.match});

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.9,
      builder: (context, scrollController) {
        return Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(20),
              topRight: Radius.circular(20),
            ),
          ),
          child: Column(
            children: [
              // Handle bar
              Container(
                margin: const EdgeInsets.only(top: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              
              // Header
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    const Text(
                      'Match Details',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close),
                    ),
                  ],
                ),
              ),
              
              // Content
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  children: [
                    // Match status
                    Text(
                      'Status: ${match.status}',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 12),
                    
                    // Price
                    if (match.price != null) ...[
                      Text(
                        'Price: \$${match.price!.toStringAsFixed(2)}',
                        style: const TextStyle(fontSize: 16),
                      ),
                      const SizedBox(height: 12),
                    ],
                    
                    // Match details based on which ride exists
                    if (match.rideOffer != null) ...[
                      Text(
                        'Offer Details:',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text('User: ${match.rideOffer!.profile?.fullName ?? "Unknown"}'),
                      Text('Route: ${match.rideOffer!.startLocation} → ${match.rideOffer!.endDestination}'),
                      if (match.rideOffer!.departureDatetime != null)
                        Text('Time: ${DateFormat('MMM dd, yyyy hh:mm a').format(match.rideOffer!.departureDatetime!)}'),
                      Text('Seats Available: ${match.rideOffer!.numberOfSeats}'),
                    ],
                    
                    if (match.rideRequest != null) ...[
                      Text(
                        'Request Details:',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text('User: ${match.rideRequest!.profile?.fullName ?? "Unknown"}'),
                      Text('Route: ${match.rideRequest!.startLocation} → ${match.rideRequest!.endDestination}'),
                      if (match.rideRequest!.departureDatetime != null)
                        Text('Time: ${DateFormat('MMM dd, yyyy hh:mm a').format(match.rideRequest!.departureDatetime!)}'),
                      Text('Seats Needed: ${match.rideRequest!.numberOfSeats}'),
                    ],
                    
                    const SizedBox(height: 30),
                    
                    // Action buttons
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () {
                              Navigator.pop(context);
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Contact functionality will be implemented')),
                              );
                            },
                            icon: const Icon(Icons.message),
                            label: const Text('Contact'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.blue,
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () {
                              Navigator.pop(context);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(match.isBothAccepted 
                                      ? 'This match is already confirmed!' 
                                      : 'Accept functionality will be implemented'),
                                ),
                              );
                            },
                            icon: Icon(match.isBothAccepted ? Icons.check_circle : Icons.handshake),
                            label: Text(match.isBothAccepted ? 'Confirmed' : 'Accept'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: match.isBothAccepted ? Colors.grey : Colors.green,
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}