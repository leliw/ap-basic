import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterOutlet } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { ConfigService } from './config/config.service';
import { GoogleSigninButtonModule, SocialAuthService, SocialUser } from '@abacritt/angularx-social-login';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

export interface Hello {
    Hello: string;
}
@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterOutlet, HttpClientModule, RouterModule, MatToolbarModule, MatIconModule, MatButtonModule, GoogleSigninButtonModule],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})

export class AppComponent {

    user: SocialUser | null = null;
    loggedIn: boolean = false;

    title = 'frontend';
    hello = '';
    version = '';

    constructor(private http: HttpClient, private authService: SocialAuthService, private config: ConfigService) {
        this.http.get<Hello>('/api').subscribe(data => {
            this.hello = data.Hello;
        });
        this.config.getConfig().subscribe(c => {
            this.title = c.title;
            this.version = c.version;
        })
    }

    ngOnInit() {
        this.authService.authState.subscribe((user) => {
            this.user = user;
            this.loggedIn = (user != null);
        });
    }

    signOut(): void {
        this.authService.signOut();
        this.user = null;
        this.loggedIn = false;
    }

}
