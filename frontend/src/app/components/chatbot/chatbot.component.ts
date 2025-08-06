import {
  Component,
  ViewChild,
  ElementRef,
  AfterViewChecked,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PortfolioService } from '../../services/portfolio.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
})
export class ChatbotComponent implements AfterViewChecked {
  @ViewChild('messagesContainer')
  private messagesContainer!: ElementRef<HTMLDivElement>;

  isOpen = false;
  newMessage = '';
  loading = false;
  messages: { from: string; text: string; html?: SafeHtml }[] = [];

  constructor(
    private portfolioService: PortfolioService,
    private sanitizer: DomSanitizer
  ) {}

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    try {
      const el = this.messagesContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    } catch {}
  }

  async sendMessage() {
    const userInput = this.newMessage.trim();
    if (!userInput) return;

    this.messages.push({ from: 'You', text: userInput });
    this.newMessage = '';
    this.loading = true;

    this.portfolioService.getChatbotResponse(userInput).subscribe({
      next: async (response) => {
        const raw = response.answer;
        const parsed = await marked.parse(raw);
        const html = this.sanitizer.bypassSecurityTrustHtml(parsed);
        this.messages.push({ from: 'AI', text: raw, html });
        this.loading = false;
      },
      error: (err) => {
        this.messages.push({
          from: 'AI',
          text: 'Something went wrong. Please try again.',
        });
        this.loading = false;
        console.error('Chatbot error:', err);
      },
    });
  }

  autoGrow(event: Event): void {
    const ta = event.target as HTMLTextAreaElement;
    ta.style.height = 'auto';
    ta.style.height = ta.scrollHeight + 'px';
  }
}
