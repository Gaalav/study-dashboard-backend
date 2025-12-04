from django.apps import AppConfig
import os


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        # Create users from environment variables on startup
        # Format: DASHBOARD_USERS = "username1:password1,username2:password2"
        # Or single user: DASHBOARD_USERNAME and DASHBOARD_PASSWORD
        from django.contrib.auth.models import User
        
        try:
            # Method 1: Multiple users via DASHBOARD_USERS
            users_str = os.environ.get('DASHBOARD_USERS', '')
            if users_str:
                for user_pair in users_str.split(','):
                    if ':' in user_pair:
                        username, password = user_pair.strip().split(':', 1)
                        self._create_or_update_user(User, username, password)
            
            # Method 2: Single user via DASHBOARD_USERNAME/PASSWORD
            username = os.environ.get('DASHBOARD_USERNAME')
            password = os.environ.get('DASHBOARD_PASSWORD')
            if username and password:
                self._create_or_update_user(User, username, password)
                
        except Exception as e:
            print(f"Could not create users: {e}")
    
    def _create_or_update_user(self, User, username, password):
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(username=username, password=password)
            print(f"Created user: {username}")
        else:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            print(f"Updated password for user: {username}")

