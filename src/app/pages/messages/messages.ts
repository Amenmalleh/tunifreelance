import { Component, inject, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
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
import { MessageService, Message, UserSearchResult } from '../../services/message.service';
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
export class Messages implements OnInit, AfterViewChecked {
  private messageService = inject(MessageService);
  private authService = inject(AuthService);
  private snackBar = inject(MatSnackBar);

  @ViewChild('messagesList') messagesList!: ElementRef;

  messages: Message[] = [];
  conversations: Map<number, Conversation> = new Map();
  selectedConversationId: number | null = null;
  currentMessage = '';
  isLoading = true;
  currentUserId: number | null = null;

  // User search for new conversations
  userSearchQuery = '';
  userSearchResults: UserSearchResult[] = [];
  isSearching = false;
  showUserSearch = false;
  private shouldScrollToBottom = false;

  ngOnInit() {
    this.currentUserId = this.authService.getCurrentUserId();
    this.loadMessages();
  }

  ngAfterViewChecked() {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
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
      const otherUserName = msg.sender_id === this.currentUserId ? msg.recipient_username : msg.sender;

      if (!this.conversations.has(otherUserId)) {
        this.conversations.set(otherUserId, {
          user_id: otherUserId,
          user_name: otherUserName,
          last_message: msg.content,
          last_message_time: msg.created_at,
          unread_count: 0
        });
      }

      const conv = this.conversations.get(otherUserId)!;
      // Keep the most recent message
      if (new Date(msg.created_at) > new Date(conv.last_message_time)) {
        conv.last_message = msg.content;
        conv.last_message_time = msg.created_at;
      }

      // Update unread count if message is unread and for current user
      if (!msg.is_read && msg.recipient_id === this.currentUserId) {
        conv.unread_count++;
      }
    });
  }

  selectConversation(userId: number) {
    this.selectedConversationId = userId;
    this.showUserSearch = false;
    this.shouldScrollToBottom = true;

    // Mark messages as read
    this.messageService.markConversationRead(userId).subscribe();

    // Update local unread count
    const conv = this.conversations.get(userId);
    if (conv) {
      conv.unread_count = 0;
    }
  }

  getConversationMessages(userId: number): Message[] {
    return this.messages.filter(msg =>
      (msg.sender_id === this.currentUserId && msg.recipient_id === userId) ||
      (msg.sender_id === userId && msg.recipient_id === this.currentUserId)
    ).sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
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
        this.shouldScrollToBottom = true;
      },
      error: (err) => {
        console.error('Error sending message:', err);
        this.snackBar.open('Error sending message.', 'Close', { duration: 4000 });
      }
    });
  }

  // User search
  toggleUserSearch() {
    this.showUserSearch = !this.showUserSearch;
    this.userSearchQuery = '';
    this.userSearchResults = [];
  }

  searchUsers() {
    if (this.userSearchQuery.length < 2) {
      this.userSearchResults = [];
      return;
    }

    this.isSearching = true;
    this.messageService.searchUsers(this.userSearchQuery).subscribe({
      next: (results) => {
        this.userSearchResults = results;
        this.isSearching = false;
      },
      error: () => {
        this.isSearching = false;
      }
    });
  }

  startConversation(user: UserSearchResult) {
    // Add to conversations if not already there
    if (!this.conversations.has(user.id)) {
      this.conversations.set(user.id, {
        user_id: user.id,
        user_name: user.first_name && user.last_name
          ? `${user.first_name} ${user.last_name}`
          : user.username,
        last_message: '',
        last_message_time: new Date().toISOString(),
        unread_count: 0
      });
    }
    this.selectConversation(user.id);
  }

  private scrollToBottom() {
    try {
      if (this.messagesList) {
        this.messagesList.nativeElement.scrollTop = this.messagesList.nativeElement.scrollHeight;
      }
    } catch (err) {}
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
