import { Component, signal } from '@angular/core';
import { HttpClient, provideHttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, CommonModule],
  template: `
  <main class="container">
    <h2>Upload your resume</h2>
    <form (submit)="onSubmit($event)">
      <input type="email" [(ngModel)]="email" name="email" placeholder="Your email" required />
      <input type="file" (change)="onFileSelected($event)" accept=".pdf" required />
      <button type="submit">Upload</button>
    </form>
    <p>{{ status() }}</p>
  </main>
`
})
export class App {
  email = '';
  selectedFile: File | null = null;
  status = signal('');

  constructor(private http: HttpClient) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  onSubmit(event: Event) {
    event.preventDefault();
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('email', this.email);
    formData.append('file', this.selectedFile);

    this.status.set('Uploading...');

    this.http.post('http://localhost:8000/upload-resume', formData)
      .subscribe({
        next: (res) => {
          console.log('SUCCESS:', res);
          this.status.set('Done: ' + JSON.stringify(res));
        },
        error: (err) => {
          console.log('ERROR:', err);
          this.status.set('Error: ' + err.message);
        }
      });
  }
}