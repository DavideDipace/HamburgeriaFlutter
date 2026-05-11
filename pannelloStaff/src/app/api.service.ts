import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  // Assicurati che l'URL coincida con quello in cui gira il tuo Flask
  private baseUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) { }

  // --- GESTIONE ORDINI ---
  getOrdini(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/ordini`);
  }

  updateStatoOrdine(id: number, nuovoStato: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/ordini/${id}`, { stato: nuovoStato });
  }

  // --- GESTIONE MENU ---
  getMenu(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/menu`);
  }

  addProdotto(prodotto: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/menu`, prodotto);
  }

  // NUOVO: Metodo per la modifica
  updateProdotto(id: number, prodotto: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/menu/${id}`, prodotto);
  }

  deleteProdotto(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/menu/${id}`);
  }
}