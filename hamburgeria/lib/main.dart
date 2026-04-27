import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() {
  runApp(const HamburgeriaTotem());
}

class HamburgeriaTotem extends StatelessWidget {
  const HamburgeriaTotem({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Totem Hamburgeria',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.orange),
      ),
      home: const HomePage(),
    );
  }
}

// Modello Prodotto 
class Product {
  final int id;
  final String name;
  final double price;
  final String category;

  Product({required this.id, required this.name, required this.price, required this.category});

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      name: json['nome'],
      price: json['prezzo'].toDouble(),
      category: json['categoria'],
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<Product> menu = [];
  List<Product> cart = [];
  bool isLoading = true;

  final String apiUrl = "http://127.0.0.1:5000"; 

  @override
  void initState() {
    super.initState();
    fetchMenu();
  }

  // Recupera il menù (Dati Finti per simulare il backend)
  Future<void> fetchMenu() async {
    await Future.delayed(const Duration(seconds: 1)); 

    setState(() {
      menu = [
        Product(id: 1, name: 'Cheeseburger', price: 8.50, category: 'Panini'),
        Product(id: 2, name: 'Bacon Burger', price: 9.50, category: 'Panini'),
        Product(id: 3, name: 'Chicken Burger', price: 8.00, category: 'Panini'),
        Product(id: 4, name: 'Patatine Fritte', price: 4.00, category: 'Appetizer'),
        Product(id: 5, name: 'Anelli di Cipolla', price: 5.00, category: 'Appetizer'),
        Product(id: 6, name: 'Nuggets (6pz)', price: 5.50, category: 'Appetizer'),
        Product(id: 7, name: 'Coca Cola', price: 3.00, category: 'Bevande'),
        Product(id: 8, name: 'Acqua Naturale', price: 1.50, category: 'Bevande'),
      ];
      isLoading = false;
    });
  }

  // Invia l'ordine al backend Flask
  Future<void> sendOrder() async {
    if (cart.isEmpty) return;

    try {
      final response = await http.post(
        Uri.parse('$apiUrl/ordini'),
        headers: {"Content-Type": "application/json"},
        body: json.encode({
          "prodotti": cart.map((p) => p.id).toList(),
          "totale": cart.fold(0.0, (sum, item) => sum + item.price),
        }),
      );

      if (!mounted) return;

      if (response.statusCode == 201) {
        showSuccessDialog();
        setState(() => cart.clear());
      }
    } catch (e) {
      if (!mounted) return; 
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Errore nell'invio dell'ordine")),
      );
    }
  }

  void showSuccessDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Ordine Inviato!"),
        content: const Text("Il tuo ordine è in fase di preparazione."),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text("OK"))
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("La Vostra Hamburgeria - Totem"),
        backgroundColor: Colors.orange,
        actions: [
          Stack(
            alignment: Alignment.center,
            children: [
              IconButton(
                icon: const Icon(Icons.shopping_basket, size: 30),
                onPressed: () => _showCartSheet(),
              ),
              if (cart.isNotEmpty)
                Positioned(
                  right: 8,
                  top: 8,
                  child: CircleAvatar(
                    radius: 10,
                    backgroundColor: Colors.red,
                    child: Text(cart.length.toString(), style: const TextStyle(fontSize: 12, color: Colors.white)),
                  ),
                )
            ],
          )
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              children: [
                _buildCategorySection("Panini", Icons.lunch_dining),
                _buildCategorySection("Appetizer", Icons.tapas),
                _buildCategorySection("Bevande", Icons.local_drink),
              ],
            ),
    );
  }

  Widget _buildCategorySection(String category, IconData icon) {
    final items = menu.where((p) => p.category.toLowerCase() == category.toLowerCase()).toList();
    if (items.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Icon(icon, color: Colors.orange),
              const SizedBox(width: 10),
              Text(category, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            ],
          ),
        ),
        SizedBox(
          height: 180,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: items.length,
            itemBuilder: (context, index) {
              final product = items[index];
              return Container(
                width: 160,
                margin: const EdgeInsets.only(left: 16),
                child: Card(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.fastfood, size: 40, color: Colors.grey),
                      Text(product.name, textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold)),
                      Text("€${product.price.toStringAsFixed(2)}"),
                      ElevatedButton(
                        onPressed: () {
                          setState(() => cart.add(product));
                          _showCartSheet(); 
                        },
                        child: const Text("Aggiungi"),
                      )
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  void _showCartSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setModalState) {
            double total = cart.fold(0, (sum, item) => sum + item.price);
            return Container(
              padding: const EdgeInsets.all(16.0),
              height: MediaQuery.of(context).size.height * 0.7, // Leggermente più alto per comodità
              child: Column(
                children: [
                  const Text("Il Tuo Ordine Completo", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  const Divider(),
                  Expanded(
                    child: cart.isEmpty 
                      ? const Center(child: Text("Il tuo carrello è vuoto"))
                      : ListView.builder(
                          itemCount: cart.length,
                          itemBuilder: (context, index) => ListTile(
                            leading: const Icon(Icons.check_circle, color: Colors.green),
                            title: Text(cart[index].name),
                            subtitle: Text("€${cart[index].price.toStringAsFixed(2)}"),
                            // MODIFICA: Aggiunta tasto per rimuovere il prodotto
                            trailing: IconButton(
                              icon: const Icon(Icons.delete_outline, color: Colors.red),
                              onPressed: () {
                                setModalState(() {
                                  cart.removeAt(index);
                                });
                                // Aggiorna anche lo stato della HomePage (per il badge in alto)
                                setState(() {});
                              },
                            ),
                          ),
                        ),
                  ),
                  const Divider(),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text("TOTALE:", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      Text("€${total.toStringAsFixed(2)}", style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.orange)),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text("CONTINUA ACQUISTI"),
                        ),
                      ),
                      const SizedBox(width: 10),
                      if (cart.isNotEmpty)
                        Expanded(
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(backgroundColor: Colors.orange, foregroundColor: Colors.white),
                            onPressed: () {
                              Navigator.pop(context);
                              sendOrder();
                            },
                            child: const Text("INVIA ORDINE"),
                          ),
                        ),
                    ],
                  )
                ],
              ),
            );
          }
        );
      },
    );
  }
}