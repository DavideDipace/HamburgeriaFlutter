import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-menu-admin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  styles: [`
    .form-container { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    input, select { margin-right: 10px; padding: 8px; }
    button { padding: 8px 15px; cursor: pointer; }
    .btn-save { background: #28a745; color: white; border: none; }
    .btn-edit { background: #ffc107; border: none; margin-right: 5px; }
    .btn-delete { background: #dc3545; color: white; border: none; }
    .item-row { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ddd; }
  `],
  template: `
    <div>
      <h2>Gestione Menù</h2>
      
      <div class="form-container">
        <h3>{{ isModifica ? 'Modifica Prodotto' : 'Aggiungi Nuovo Prodotto' }}</h3>
        <input [(ngModel)]="formProdotto.nome" placeholder="Nome prodotto">
        <input [(ngModel)]="formProdotto.prezzo" type="number" placeholder="Prezzo (€)">
        <select [(ngModel)]="formProdotto.categoria">
          <option value="panini">Panini</option>
          <option value="appetizer">Appetizer</option>
          <option value="bevande">Bevande</option>
          <option value="menu">Menu Completi</option>
        </select>

        <button *ngIf="!isModifica" class="btn-save" (click)="salvaProdotto()">Aggiungi</button>
        
        <ng-container *ngIf="isModifica">
          <button class="btn-save" (click)="salvaModifica()">Salva Modifiche</button>
          <button (click)="annullaModifica()" style="margin-left: 10px;">Annulla</button>
        </ng-container>
      </div>

      <div *ngFor="let p of prodotti" class="item-row">
        <span><strong>{{p.nome}}</strong> ({{p.categoria}}) - €{{p.prezzo | number:'1.2-2'}}</span>
        <div>
          <button class="btn-edit" (click)="preparaModifica(p)">Modifica</button>
          <button class="btn-delete" (click)="elimina(p.id)">Elimina</button>
        </div>
      </div>
    </div>
  `
})
export class MenuAdminComponent implements OnInit {
  prodotti: any[] = [];
  
  // Stato del form
  formProdotto = { id: null, nome: '', prezzo: null, categoria: 'panini' };
  isModifica = false;

  constructor(private api: ApiService) {}

  ngOnInit() { this.caricaMenu(); }

  caricaMenu() {
    this.api.getMenu().subscribe(data => this.prodotti = data);
  }

  salvaProdotto() {
    this.api.addProdotto(this.formProdotto).subscribe(() => {
      this.caricaMenu();
      this.resetForm();
    });
  }

  // Prepara il form per la modifica riempiendolo con i dati attuali
  preparaModifica(prodotto: any) {
    this.isModifica = true;
    this.formProdotto = { ...prodotto }; // Clona i dati
  }

  salvaModifica() {
    if (this.formProdotto.id) {
      this.api.updateProdotto(this.formProdotto.id, this.formProdotto).subscribe(() => {
        this.caricaMenu();
        this.resetForm();
      });
    }
  }

  annullaModifica() {
    this.resetForm();
  }

  elimina(id: number) {
    if(confirm("Sei sicuro di voler eliminare questo prodotto?")) {
      this.api.deleteProdotto(id).subscribe(() => this.caricaMenu());
    }
  }

  resetForm() {
    this.isModifica = false;
    this.formProdotto = { id: null, nome: '', prezzo: null, categoria: 'panini' };
  }
}