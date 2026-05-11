import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-orders',
  standalone: true,
  imports: [CommonModule],
  styles: [`
    .order-card { border: 2px solid #ffa500; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fffaf0; }
    .status-badge { padding: 5px 10px; border-radius: 20px; font-weight: bold; background: #ffc107; }
    .btn-status { background: #17a2b8; color: white; border: none; padding: 8px 15px; cursor: pointer; margin-right: 10px; margin-top: 10px;}
    .btn-complete { background: #28a745; color: white; border: none; padding: 8px 15px; cursor: pointer; margin-top: 10px;}
  `],
  template: `
    <div>
      <h2>Cucina - Ordini in Tempo Reale</h2>
      <button (click)="caricaOrdini()" style="margin-bottom: 15px;">Aggiorna Ordini</button>

      <div *ngIf="ordini.length === 0">Nessun ordine in corso al momento.</div>

      <div *ngFor="let ordine of ordini" class="order-card">
        <h3>Ordine #{{ordine.id}} <span class="status-badge">{{ordine.stato}}</span></h3>
        <p><strong>Totale:</strong> €{{ordine.totale}}</p>
        
        <h4>Prodotti da preparare:</h4>
        <ul>
          <li *ngFor="let p of ordine.prodotti">{{p.nome}}</li>
        </ul>
        
        <button class="btn-status" (click)="cambiaStato(ordine.id, 'In Preparazione')">Segna "In Preparazione"</button>
        <button class="btn-complete" (click)="cambiaStato(ordine.id, 'Completato')">Segna "Completato"</button>
      </div>
    </div>
  `
})
export class OrdersComponent implements OnInit {
  ordini: any[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() { this.caricaOrdini(); }

  caricaOrdini() {
    this.api.getOrdini().subscribe(data => {
      // Opzionale: Filtra per nascondere gli ordini già completati
      this.ordini = data.filter(o => o.stato !== 'Completato');
    });
  }

  cambiaStato(id: number, nuovoStato: string) {
    this.api.updateStatoOrdine(id, nuovoStato).subscribe(() => {
      this.caricaOrdini(); // Ricarica la lista per aggiornare la UI
    });
  }
}