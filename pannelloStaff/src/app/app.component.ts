import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OrdersComponent } from './orders/orders.component';
import { MenuAdminComponent } from './menu-admin/menu-admin.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, OrdersComponent, MenuAdminComponent],
  styles: [`
    .navbar { background: #343a40; padding: 15px; color: white; display: flex; gap: 20px; }
    .nav-btn { background: none; color: white; border: none; font-size: 16px; cursor: pointer; padding: 5px 10px; }
    .nav-btn.active { border-bottom: 2px solid orange; font-weight: bold; }
    .content { padding: 20px; max-width: 1000px; margin: auto; }
  `],
  template: `
    <div class="navbar">
      <h2>🍔 Hamburgeria Staff</h2>
      <div style="margin-left: 50px; display: flex; align-items: center;">
        <button class="nav-btn" [class.active]="view === 'ordini'" (click)="view = 'ordini'">Cucina (Ordini)</button>
        <button class="nav-btn" [class.active]="view === 'menu'" (click)="view = 'menu'">Gestione Menù</button>
      </div>
    </div>

    <div class="content">
      <app-orders *ngIf="view === 'ordini'"></app-orders>
      <app-menu-admin *ngIf="view === 'menu'"></app-menu-admin>
    </div>
  `
})
export class AppComponent {
  view: 'ordini' | 'menu' = 'ordini';
}