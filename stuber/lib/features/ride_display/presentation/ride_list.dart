import 'package:flutter/material.dart';

class RideList extends StatelessWidget {
  const RideList({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ride list'),
      ),
      body: const Center(
        child: Text('Display all user rides here'),
      ),
    );
  }
}