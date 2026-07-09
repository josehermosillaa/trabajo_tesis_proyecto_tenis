import { Component, OnInit, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { HealthService } from './core/services/health.service';
import { HealthResponse } from './core/models/health-response.model';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {

  private healthService = inject(HealthService);

  health?: HealthResponse;

  ngOnInit(): void {
    this.healthService.getHealth().subscribe({
      next: (response) => {
        console.log(response);
        this.health = response;
      },
      error: (error) => {
        console.error(error);
      },
    });
  }
}