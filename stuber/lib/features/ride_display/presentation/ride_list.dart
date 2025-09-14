import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:stuber/features/ride_display/presentation/ride_model.dart';
import 'package:stuber/features/ride_display/presentation/ride_card.dart';
import 'package:stuber/features/ride_display/presentation/ride_detail_screen.dart';
import 'package:stuber/features/ride_display/data/unified_ride_repository_v1.dart';

class RideList extends StatefulWidget {
  const RideList({Key? key}) : super(key: key);

  @override
  State<RideList> createState() => _RideListState();
}

class _RideListState extends State<RideList> {
  final UnifiedRideRepository _repository = UnifiedRideRepository();
  late Future<List<RideItem>> _ridesFuture;
  String _selectedView = 'my_rides'; // my_rides, all_rides
  RideType? _selectedFilter; // null = all, request, offer

  @override
  void initState() {
    super.initState();
    _loadRides();
  }

  void _loadRides() {
    setState(() {
      switch (_selectedView) {
        case 'my_rides':
          if (_selectedFilter != null) {
            _ridesFuture = _repository.getRidesByType(_selectedFilter!);
          } else {
            _ridesFuture = _repository.getUserRides();
          }
          break;
        case 'all_rides':
          _ridesFuture = _repository.getAllAvailableRides();
          break;
        default:
          _ridesFuture = _repository.getUserRides();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_getAppBarTitle()),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          // Filter by ride type
          if (_selectedView == 'my_rides')
            PopupMenuButton<RideType?>(
              onSelected: (value) {
                setState(() {
                  _selectedFilter = value;
                });
                _loadRides();
              },
              itemBuilder: (context) => [
                PopupMenuItem(
                  value: null,
                  child: Row(
                    children: [
                      const Icon(Icons.list, size: 20),
                      const SizedBox(width: 8),
                      Text('All Types'),
                      if (_selectedFilter == null)
                        const Padding(
                          padding: EdgeInsets.only(left: 8),
                          child: Icon(Icons.check, size: 16, color: Colors.blue),
                        ),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: RideType.request,
                  child: Row(
                    children: [
                      const Icon(Icons.search, size: 20, color: Colors.orange),
                      const SizedBox(width: 8),
                      const Text('Requests Only'),
                      if (_selectedFilter == RideType.request)
                        const Padding(
                          padding: EdgeInsets.only(left: 8),
                          child: Icon(Icons.check, size: 16, color: Colors.blue),
                        ),
                    ],
                  ),
                ),
                PopupMenuItem(
                  value: RideType.offer,
                  child: Row(
                    children: [
                      const Icon(Icons.local_offer, size: 20, color: Colors.green),
                      const SizedBox(width: 8),
                      const Text('Offers Only'),
                      if (_selectedFilter == RideType.offer)
                        const Padding(
                          padding: EdgeInsets.only(left: 8),
                          child: Icon(Icons.check, size: 16, color: Colors.blue),
                        ),
                    ],
                  ),
                ),
              ],
              child: const Icon(Icons.filter_list),
            ),
          
          // Switch between my rides and browse all
          PopupMenuButton<String>(
            onSelected: (value) {
              setState(() {
                _selectedView = value;
                _selectedFilter = null; // Reset filter when switching views
              });
              _loadRides();
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'my_rides',
                child: Row(
                  children: [
                    const Icon(Icons.person, size: 20),
                    const SizedBox(width: 8),
                    const Text('My Rides'),
                    if (_selectedView == 'my_rides')
                      const Padding(
                        padding: EdgeInsets.only(left: 8),
                        child: Icon(Icons.check, size: 16, color: Colors.blue),
                      ),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'all_rides',
                child: Row(
                  children: [
                    const Icon(Icons.explore, size: 20),
                    const SizedBox(width: 8),
                    const Text('Browse All'),
                    if (_selectedView == 'all_rides')
                      const Padding(
                        padding: EdgeInsets.only(left: 8),
                        child: Icon(Icons.check, size: 16, color: Colors.blue),
                      ),
                  ],
                ),
              ),
            ],
            child: const Icon(Icons.menu),
          ),
          
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadRides,
          ),
        ],
      ),
      body: Column(
        children: [
          // Quick stats bar
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.grey.shade50,
            child: FutureBuilder<List<RideItem>>(
              future: _ridesFuture,
              builder: (context, snapshot) {
                if (snapshot.hasData) {
                  final rides = snapshot.data!;
                  final requests = rides.where((r) => r.rideType == RideType.request).length;
                  final offers = rides.where((r) => r.rideType == RideType.offer).length;
                  final upcomingRides = rides.where((r) => 
                    r.departureDatetime?.isAfter(DateTime.now()) ?? false
                  ).length;
                  
                  return Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _StatItem(
                        label: 'Total',
                        value: rides.length.toString(),
                        icon: Icons.list,
                        color: Colors.blue,
                      ),
                      _StatItem(
                        label: 'Requests',
                        value: requests.toString(),
                        icon: Icons.search,
                        color: Colors.orange,
                      ),
                      _StatItem(
                        label: 'Offers',
                        value: offers.toString(),
                        icon: Icons.local_offer,
                        color: Colors.green,
                      ),
                      if (_selectedView == 'my_rides')
                        _StatItem(
                          label: 'Upcoming',
                          value: upcomingRides.toString(),
                          icon: Icons.schedule,
                          color: Colors.purple,
                        ),
                    ],
                  );
                }
                return const SizedBox.shrink();
              },
            ),
          ),
          
          // Main content
          Expanded(
            child: FutureBuilder<List<RideItem>>(
              future: _ridesFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 16),
                        Text('Loading rides...'),
                      ],
                    ),
                  );
                }

                if (snapshot.hasError) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.error_outline,
                          size: 64,
                          color: Colors.red.shade300,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Error loading rides',
                          style: TextStyle(
                            fontSize: 18,
                            color: Colors.red.shade600,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 32),
                          child: Text(
                            '${snapshot.error}',
                            style: const TextStyle(
                              fontSize: 14,
                              color: Colors.grey,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadRides,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  );
                }

                final rides = snapshot.data ?? [];

                if (rides.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.directions_car,
                          size: 64,
                          color: Colors.grey.shade400,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          _getEmptyStateTitle(),
                          style: const TextStyle(
                            fontSize: 18,
                            color: Colors.grey,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _getEmptyStateSubtitle(),
                          style: const TextStyle(
                            fontSize: 14,
                            color: Colors.grey,
                          ),
                        ),
                        const SizedBox(height: 24),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            ElevatedButton.icon(
                              onPressed: () {
                                _showCreateDialog(RideType.request);
                              },
                              icon: const Icon(Icons.search),
                              label: const Text('Create Request'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.orange,
                                foregroundColor: Colors.white,
                              ),
                            ),
                            const SizedBox(width: 16),
                            ElevatedButton.icon(
                              onPressed: () {
                                _showCreateDialog(RideType.offer);
                              },
                              icon: const Icon(Icons.local_offer),
                              label: const Text('Create Offer'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.green,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                }

                return RefreshIndicator(
                  onRefresh: () async {
                    _loadRides();
                    await _ridesFuture;
                  },
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    itemCount: rides.length,
                    itemBuilder: (context, index) {
                      return RideCard(
                        rideItem: rides[index],
                        onTap: () {
                          _navigateToRideDetail(rides[index]);
                        },
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // FloatingActionButton.extended(
          //   onPressed: () => _showCreateDialog(RideType.request),
          //   heroTag: "request_fab",
          //   backgroundColor: Colors.orange,
          //   icon: const Icon(Icons.search),
          //   label: const Text('Request'),
          // ),
          const SizedBox(width: 16),
          // FloatingActionButton.extended(
          //   onPressed: () => _showCreateDialog(RideType.offer),
          //   heroTag: "offer_fab",
          //   backgroundColor: Colors.green,
          //   icon: const Icon(Icons.local_offer),
          //   label: const Text('Offer'),
          // ),
        ],
      ),
    );
  }

  String _getAppBarTitle() {
    String baseTitle = _selectedView == 'my_rides' ? 'My Rides' : 'Browse Rides';
    
    if (_selectedFilter != null) {
      String filterText = _selectedFilter == RideType.request ? 'Requests' : 'Offers';
      return '$baseTitle - $filterText';
    }
    
    return baseTitle;
  }

  String _getEmptyStateTitle() {
    if (_selectedView == 'my_rides') {
      if (_selectedFilter == RideType.request) return 'No ride requests found';
      if (_selectedFilter == RideType.offer) return 'No ride offers found';
      return 'No rides found';
    } else {
      return 'No available rides';
    }
  }

  String _getEmptyStateSubtitle() {
    if (_selectedView == 'my_rides') {
      return 'Create your first ride request or offer to get started!';
    } else {
      return 'Check back later for new ride requests and offers.';
    }
  }

  // Navigate to ride detail screen
  void _navigateToRideDetail(RideItem rideItem) async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => RideDetailScreen(rideItem: rideItem),
      ),
    );

    // If the ride was deleted (result == true), refresh the list
    if (result == true) {
      _loadRides();
    }
  }

  void _showCreateDialog(RideType rideType) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              rideType == RideType.request ? Icons.search : Icons.local_offer,
              color: rideType == RideType.request ? Colors.orange : Colors.green,
            ),
            const SizedBox(width: 8),
            Text('Create ${rideType == RideType.request ? 'Request' : 'Offer'}'),
          ],
        ),
        content: Text(
          'Create ${rideType == RideType.request ? 'ride request' : 'ride offer'} functionality will be implemented here.'
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _StatItem({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, size: 24, color: color),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }
}