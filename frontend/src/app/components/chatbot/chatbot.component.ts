import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PortfolioService } from '../../services/portfolio.service';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
})
export class ChatbotComponent {
  isOpen = false;
  newMessage = '';
  messages: { from: string; text: string }[] = [];

  constructor(private portfolioService: PortfolioService) {}

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  loading = false;

  sendMessage() {
    if (!this.newMessage.trim()) return;

    const userMessage = this.newMessage;
    this.messages.push({ from: 'You', text: userMessage });
    this.newMessage = '';

    this.loading = true; // Start loading

    this.portfolioService.getChatbotResponse(userMessage).subscribe({
      next: (response) => {
        this.loading = false; // Stop loading
        this.messages.push({ from: 'AI', text: response.answer });
      },
      error: (err) => {
        this.loading = false; // Stop loading
        this.messages.push({
          from: 'Bot',
          text: 'Something went wrong. Please try again.',
        });
        console.error('Chatbot error:', err);
      },
    });
  }
}
