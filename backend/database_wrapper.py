import pymysql
import pymysql.cursors

class DatabaseWrapper:
    def __init__(self, host, user, password, database, port):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': int(port),
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': True,
            # Aiven richiede la connessione SSL sicura
            'ssl': {} 
        }

    def _get_connection(self):
        """Stabilisce la connessione con MySQL su Aiven usando PyMySQL"""
        return pymysql.connect(**self.config)

    # ==========================================================
    # 1. GESTIONE CATEGORIE (Panini, Bevande, Menu, ecc.)
    # ==========================================================
    
    def get_categorie(self):
        """Recupera tutte le categorie disponibili nel database"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM categorie")
                return cursor.fetchall()


    # ==========================================================
    # 2. GESTIONE PRODOTTI (CRUD Completo per Angular Staff)
    # ==========================================================

    def get_prodotti(self):
        """Recupera tutti i prodotti associando il nome della loro categoria"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT p.id, p.nome, p.descrizione, p.prezzo, p.immagine, p.categoria_id, c.nome AS nome_categoria 
                    FROM prodotti p 
                    LEFT JOIN categorie c ON p.categoria_id = c.id
                """
                cursor.execute(query)
                return cursor.fetchall()

    def add_prodotto(self, nome, descrizione, prezzo, immagine, categoria_id):
        """Inserisce un nuovo prodotto nel menù (Aggiunta)"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO prodotti (nome, descrizione, prezzo, immagine, categoria_id) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (nome, descrizione, prezzo, immagine, categoria_id))
                return cursor.lastrowid

    def update_prodotto(self, prodotto_id, nome, descrizione, prezzo, immagine, categoria_id):
        """Modifica un prodotto esistente (Modifica)"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    UPDATE prodotti 
                    SET nome = %s, descrizione = %s, prezzo = %s, immagine = %s, categoria_id = %s 
                    WHERE id = %s
                """
                cursor.execute(query, (nome, descrizione, prezzo, immagine, categoria_id, prodotto_id))
                return cursor.rowcount

    def delete_prodotto(self, prodotto_id):
        """Rimuove definitivamente un prodotto dal menù (Eliminazione)"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = "DELETE FROM prodotti WHERE id = %s"
                cursor.execute(query, (prodotto_id,))
                return cursor.rowcount


    # ==========================================================
    # 3. GESTIONE ORDINI (Totem Clienti & Pannello Staff)
    # ==========================================================

    def create_ordine(self, prodotti_in_carrello):
        """
        Crea un nuovo ordine nel database.
        Riceve in input una lista di dizionari: 
        [{"prodotto_id": 1, "quantita": 2, "prezzo_unitario": 8.50}, ...]
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                # Calcola il costo totale sommando ogni riga del carrello
                totale = sum(item['quantita'] * float(item['prezzo_unitario']) for item in prodotti_in_carrello)
                
                # Inserisce l'ordine principale (stato di default: 'in_attesa')
                cursor.execute("INSERT INTO ordini (totale) VALUES (%s)", (totale,))
                ordine_id = cursor.lastrowid
                
                # Associa i singoli prodotti acquistati all'ordine appena generato
                for item in prodotti_in_carrello:
                    query_dettaglio = """
                        INSERT INTO dettagli_ordine (ordine_id, prodotto_id, quantita, prezzo_unitario) 
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query_dettaglio, (ordine_id, item['prodotto_id'], item['quantita'], item['prezzo_unitario']))
                return ordine_id

    def get_ordini(self):
        """Recupera la lista di tutti gli ordini registrati con i relativi prodotti associati"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                # Recupera gli ordini ordinati dal più recente
                cursor.execute("SELECT * FROM ordini ORDER BY data_ora DESC")
                ordini = cursor.fetchall()
                
                # Per ogni ordine, effettua una JOIN per recuperare i dettagli dei prodotti inclusi
                for ordine in ordini:
                    query_dettagli = """
                        SELECT d.quantita, d.prezzo_unitario, p.nome AS nome_prodotto
                        FROM dettagli_ordine d 
                        JOIN prodotti p ON d.prodotto_id = p.id 
                        WHERE d.ordine_id = %s
                    """
                    cursor.execute(query_dettagli, (ordine['id'],))
                    ordine['prodotti'] = cursor.fetchall()
                    # Converte l'oggetto data in stringa standard per evitare eccezioni nella serializzazione JSON
                    ordine['data_ora'] = ordine['data_ora'].strftime('%Y-%m-%d %H:%M:%S')
                
                return ordini

    def update_stato_ordine(self, ordine_id, nuovo_stato):
        """Aggiorna lo stato di avanzamento di un ordine (Cambio stato per lo Staff)"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                query = "UPDATE ordini SET stato = %s WHERE id = %s"
                cursor.execute(query, (nuovo_stato, ordine_id))
                return cursor.rowcount
