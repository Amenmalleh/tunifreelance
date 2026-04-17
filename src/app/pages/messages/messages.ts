import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MessageService, Message } from '../../services/message.service';
import { AuthService } from '../../services/auth.service';

interface Conversation {
  user_id: number;
  user_name: string;
  last_message: string;
  last_message_time: string;
  unread_count: number;
}

@Component({
  selector: 'app-messages',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatListModule,
    MatDividerModule,
    MatSnackBarModule
  ],
  templateUrl: './messages.html',
  styleUrl: './messages.css'
})
export class Messages implements OnInit {
  private messageService = inject(MessageService);
  private authService = inject(AuthService);
  private snackBar = inject(MatSnackBar);

  messages: Message[] = [];
  conversations: Map<number, Conversation> = new Map();
  selectedConversationId: number | null = null;
  currentMessage = '';
  isLoading = true;
  currentUserId: number | null = null;

  ngOnInit() {
    this.currentUserId = this.authService.getCurrentUserId();
    this.loadMessages();
  }

  loadMessages() {
    this.isLoading = true;
    this.messageService.getMessages().subscribe({
      next: (messages) => {
        this.messages = messages;
        this.buildConversations();
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading messages:', err);
        this.snackBar.open('Error loading messages.', 'Close', { duration: 4000 });
        this.isLoading = false;
      }
    });
  }

  buildConversations() {
    this.conversations.clear();

    this.messages.forEach(msg => {
      const otherUserId = msg.sender_id === this.currentUserId ? msg.recipient_id : msg.sender_id;
      const otherUserName = msg.sender_id === this.currentUserId ? msg.recipient : msg.sender;

      if (!this.conversations.has(otherUserId)) {
        this.conversations.set(otherUserId, {
          user_id: otherUserId,
          user_name: otherUserName,
          last_message: msg.content,
          last_message_time: msg.created_at,
          unread_count: 0
        });
      }

      // Update unread count if message is unread and for current user
      if (!msg.is_read && msg.recipient_id === this.currentUserId) {
        const conv = this.conversations.get(otherUserId)!;
        conv.unread_count++;
      }
    });
  }

  selectConversation(userId: number) {
    this.selectedConversationId = userId;
  }

  getConversationMessages(userId: number): Message[] {
    return this.messages.filter(msg =>
      (msg.sender_id === this.currentUserId && msg.recipient_id === userId) ||
      (msg.sender_id === userId && msg.recipient_id === this.currentUserId)
    );
  }

  getConversationUserIds(): number[] {
    return Array.from(this.conversations.keys());
  }

  getConversation(userId: number): Conversation | undefined {
    return this.conversations.get(userId);
  }

  getConversationName(userId: number): string {
    return this.conversations.get(userId)?.user_name || 'Unknown';
  }

  sendMessage() {
    if (!this.selectedConversationId || !this.currentMessage.trim()) {
      return;
    }

    this.messageService.sendMessage({
      recipient: this.selectedConversationId,
      content: this.currentMessage
    }).subscribe({
      next: () => {
        this.currentMessage = '';
        this.loadMessages();
        this.snackBar.open('Message sent!', 'Close', { duration: 3000 });
      },
      error: (err) => {
        console.error('Error sending message:', err);
        this.snackBar.open('Error sending message.', 'Close', { duration: 4000 });
      }
    });
  }

  formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
}
