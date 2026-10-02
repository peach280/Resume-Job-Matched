import { Component, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, CommonModule],
  template: `
    <div class="page">
      <header class="masthead">
        <span class="mark">JM</span>
        <span class="tagline">resume in, matches out</span>
      </header>

      <main class="layout">
        <section class="intro">
          <h1>We read your resume<br>so job listings don't have to.</h1>
          <p class="lede">
            Upload a PDF once. Every day, new software engineering roles
            get compared against your profile and the ones worth your time
            land in your inbox.
          </p>

          <dl class="pipeline">
            <div class="step">
              <dt>01</dt>
              <dd>Resume parsed and summarized</dd>
            </div>
            <div class="step">
              <dt>02</dt>
              <dd>Compared against today's listings</dd>
            </div>
            <div class="step">
              <dt>03</dt>
              <dd>Relevant matches emailed to you</dd>
            </div>
          </dl>
        </section>

        <section class="panel">
          <form (submit)="onSubmit($event)">
            <label>
              <span>Email</span>
              <input type="email" [(ngModel)]="email" name="email" placeholder="you@domain.com" required />
            </label>

            <label>
              <span>Resume</span>
              <input type="file" (change)="onFileSelected($event)" accept=".pdf" required />
              <span class="hint">PDF only</span>
            </label>

            <button type="submit" [disabled]="isUploading()">
              {{ isUploading() ? 'Sending…' : 'Submit resume' }}
            </button>
          </form>

          <p class="status" *ngIf="status()" [class.error]="isError()">{{ status() }}</p>
        </section>
      </main>

      <footer class="foot">
        <span>No spam. No resale of your data. Unsubscribe anytime.</span>
      </footer>
    </div>
  `,
  styles: [`
    :host { display: block; min-height: 100vh; }

    .page {
      max-width: 920px;
      margin: 0 auto;
      padding: 48px 24px 64px;
      color: #1A1D1F;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .masthead {
      display: flex;
      align-items: baseline;
      gap: 10px;
      margin-bottom: 64px;
      border-bottom: 1px solid #E3E1DC;
      padding-bottom: 16px;
    }

    .mark {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      font-size: 14px;
      letter-spacing: 0.02em;
      color: #3D5A50;
      border: 1px solid #3D5A50;
      padding: 2px 7px;
    }

    .tagline {
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      color: #8A8D91;
    }

    .layout {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 56px;
      align-items: start;
    }

    @media (max-width: 760px) {
      .layout { grid-template-columns: 1fr; gap: 40px; }
    }

    h1 {
      font-family: 'Source Serif 4', Georgia, serif;
      font-size: 34px;
      line-height: 1.22;
      font-weight: 600;
      letter-spacing: -0.01em;
      margin: 0 0 20px;
      max-width: 22ch;
    }

    .lede {
      font-size: 16px;
      line-height: 1.6;
      color: #4A4E52;
      max-width: 42ch;
      margin: 0 0 40px;
    }

    .pipeline { margin: 0; display: flex; flex-direction: column; gap: 14px; }
    .step { display: flex; gap: 14px; align-items: baseline; }
    .step dt { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #3D5A50; width: 20px; flex-shrink: 0; }
    .step dd { margin: 0; font-size: 14.5px; color: #4A4E52; }

    .panel { border-left: 2px solid #3D5A50; padding-left: 28px; }

    form { display: flex; flex-direction: column; gap: 20px; }

    label { display: flex; flex-direction: column; gap: 6px; font-size: 13px; font-weight: 500; color: #1A1D1F; }

    input[type="email"] {
      font-family: inherit;
      font-size: 15px;
      padding: 10px 12px;
      border: 1px solid #D4D1CA;
      background: #FFFFFF;
      color: #1A1D1F;
      outline: none;
    }

    input[type="email"]:focus { border-color: #3D5A50; box-shadow: 0 0 0 1px #3D5A50; }

    input[type="file"] { font-family: 'JetBrains Mono', monospace; font-size: 13px; }

    .hint { font-size: 11.5px; color: #8A8D91; font-weight: 400; }

    button {
      font-family: 'JetBrains Mono', monospace;
      font-size: 13.5px;
      font-weight: 600;
      letter-spacing: 0.01em;
      background: #1A1D1F;
      color: #FAFAF8;
      border: none;
      padding: 12px 18px;
      cursor: pointer;
      width: fit-content;
      transition: background 0.15s ease;
    }

    button:hover:not(:disabled) { background: #3D5A50; }
    button:disabled { opacity: 0.5; cursor: default; }

    .status { margin-top: 18px; font-size: 13.5px; color: #3D5A50; }
    .status.error { color: #B3432D; }

    .foot {
      margin-top: 72px;
      padding-top: 20px;
      border-top: 1px solid #E3E1DC;
      font-size: 12px;
      color: #8A8D91;
    }
  `]
})
export class App {
  email = '';
  selectedFile: File | null = null;
  status = signal('');
  isUploading = signal(false);
  isError = signal(false);

  constructor(private http: HttpClient) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  onSubmit(event: Event) {
    event.preventDefault();
    if (!this.selectedFile) return;

    this.isUploading.set(true);
    this.isError.set(false);
    this.status.set('');

    const formData = new FormData();
    formData.append('email', this.email);
    formData.append('file', this.selectedFile);

    this.http.post(`${environment.apiUrl}/upload-resume`, formData)
      .subscribe({
        next: () => {
          this.isUploading.set(false);
          this.status.set("Resume received — matches will land in your inbox soon.");
        },
        error: (err) => {
          this.isUploading.set(false);
          this.isError.set(true);
          this.status.set("Something went wrong on our end. Try again in a moment.");
          console.error(err);
        }
      });
  }
}