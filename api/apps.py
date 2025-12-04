from django.apps import AppConfig
import os


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        # Create default user from environment variables on startup
        from django.contrib.auth.models import User
        
        username = os.environ.get('DASHBOARD_USERNAME')
        password = os.environ.get('DASHBOARD_PASSWORD')
        
        if username and password:
            try:
                if not User.objects.filter(username=username).exists():
                    User.objects.create_user(username=username, password=password)
                    print(f"Created user: {username}")
                else:
                    # Update password if user exists
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.save()
                    print(f"Updated password for user: {username}")
            except Exception as e:
                print(f"Could not create user: {e}")
