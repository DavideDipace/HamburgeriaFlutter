from flask import Flask, jsonify, request
from flask_cors import CORS
from database import DatabaseWrapper

app = Flask(__name__)
# Abilita le chiamate cross-origin per permettere l'accesso da Angular (porta 4200) e Flutter
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ==========================================================
# CONFIGURAZIONE CREDENZIALI DEL DATABASE MYSQL SU AIVEN
# ==========================================================
DB_HOST = "IL_TUO_HOST_DI_AIVEN.aivencloud.com"
DB_PORT = 12345  # Inserite la porta numerica a 5 cifre indicata su Aiven
DB_USER = "avnadmin"
DB_PASSWORD = "LA_TUA_PASSWORD_DI_AIVEN"
DB_NAME = "defaultdb"

# Istanziamo la classe Wrapper del Database passandogli i parametri sopra definiti
db = DatabaseWrapper(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)


# ==========================================================
# API 1: CATEGORIE (Totem & Staff)
# ==========================================================

@app.route('/api/categorie', methods=['GET'])
def api_get_categorie():
    """Restituisce l'elenco delle categorie (panini, bevande, menu, sfiziosita...)"""
    try:
        categorie = db.get_categorie()
        return jsonify(categorie), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
# API 2: PRODOTTI / MENÙ (CRUD COMPLETO)
# ==========================================================

@app.route('/api/prodotti', methods=['GET'])
def api_get_prodotti():
    """Restituisce il menù completo dei prodotti"""
    try:
        prodotti = db.get_prodotti()
        return jsonify(prodotti), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/prodotti', methods=['POST'])
def api_add_prodotto():
    """Aggiunge un nuovo prodotto al menù (Angular Staff)"""
    try:
        data = request.json
        # Validazione dei campi indispensabili
        if not all(k in data for k in ('nome', 'prezzo', 'categoria_id')):
            return jsonify({"error": "Campi obbligatori mancanti: nome, prezzo, categoria_id"}), 400
        
        nuovo_id = db.add_prodotto(
            nome=data['nome'],
            descrizione=data.get('descrizione', ''),
            prezzo=data['prezzo'],
            immagine=data.get('immagine', ''),
            categoria_id=data['categoria_id']
        )
        return jsonify({"message": "Prodotto aggiunto con successo", "id": nuovo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/prodotti/<int:prodotto_id>', methods=['PUT'])
def api_update_prodotto(prodotto_id):
    """Modifica un prodotto esistente nel menù (Angular Staff)"""
    try:
        data = request.json
        if not all(k in data for k in ('nome', 'prezzo', 'categoria_id')):
            return jsonify({"error": "Parametri obbligatori mancanti per la modifica"}), 400
        
        db.update_prodotto(
            prodotto_id=prodotto_id,
            nome=data['nome'],
            descrizione=data.get('descrizione', ''),
            prezzo=data['prezzo'],
            immagine=data.get('immagine', ''),
            categoria_id=data['categoria_id']
        )
        return jsonify({"message": "Prodotto aggiornato correttamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/prodotti/<int:prodotto_id>', methods=['DELETE'])
def api_delete_prodotto(prodotto_id):
    """Rimuove un prodotto dal menù (Angular Staff)"""
    try:
        righe_eliminate = db.delete_prodotto(prodotto_id)
        if righe_eliminate == 0:
            return jsonify({"error": "Prodotto non trovato"}), 404
        return jsonify({"message": "Prodotto rimosso con successo"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
# API 3: ORDINI (Totem & Staff)
# ==========================================================

@app.route('/api/ordini', methods=['GET'])
def api_get_ordini():
    """Restituisce tutti gli ordini registrati con la lista dei prodotti (Pannello Staff Angular)"""
    try:
        ordini = db.get_ordini()
        return jsonify(ordini), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ordini', methods=['POST'])
def api_create_ordine():
    """Riceve e registra un nuovo ordine dal totem (Totem Flutter)"""
    try:
        data = request.json
        if not data or 'prodotti' not in data:
            return jsonify({"error": "Carrello vuoto o non strutturato correttamente"}), 400
        
        ordine_id = db.create_ordine(data['prodotti'])
        return jsonify({"message": "Ordine ricevuto e inviato in cucina!", "ordine_id": ordine_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ordini/<int:ordine_id>/stato', methods=['PATCH'])
def api_update_stato(ordine_id):
    """Modifica lo stato di un ordine in corso (Pannello Staff Angular)"""
    try:
        data = request.json
        nuovo_stato = data.get('stato')
        stati_ammessi = ['in_attesa', 'in_preparazione', 'pronto', 'consegnato']
        
        if nuovo_stato not in stati_ammessi:
            return jsonify({"error": f"Stato non valido. Valori ammessi: {stati_ammessi}"}), 400
            
        db.update_stato_ordine(ordine_id, nuovo_stato)
        return jsonify({"message": f"Stato dell'ordine #{ordine_id} modificato in '{nuovo_stato}'"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Avvia l'applicazione in modalità debug sulla porta 5000 in ascolto per ogni host esterno
    app.run(host='0.0.0.0', port=5000, debug=True)