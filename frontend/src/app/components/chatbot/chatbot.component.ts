import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

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

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  sendMessage() {
    if (!this.newMessage.trim()) return;

    this.messages.push({ from: 'You', text: this.newMessage });

    // Simulate bot response (you can replace with API call)
    setTimeout(() => {
      this.messages.push({ from: 'Bot', text: `Echo: ${this.newMessage}` });
    }, 500);

    this.newMessage = '';
  }
}
