### Via Django Admin

1. Go to Django Admin (`/admin/`)
2. Navigate to "OAuth2 Provider" → "Applications"
3. Click "Add Application"
4. Configure as follows:

- **Client ID**: Will be auto-generated (use this in your Quasar app)
- **User**: (leave empty for public app or select a user)
- **Redirect URIs**:
  ```
  http://localhost:9000/auth/callback
  http://localhost:4000/auth/callback
  https://your-domain.com/auth/callback
  ```
  (One per line, add all environments)
- **Client Type**: Select **"Public"** (important for PKCE flow)
- **Authorization Grant Type**: Select **"Authorization code"**
- **Client Secret**: Leave empty (public clients don't use secrets)
- **Name**: "Cohiva PWA" (or your app name)
- **Skip Authorization**: Check if you want to skip the consent screen
- **Algorithm**: Leave as "No OIDC support" or select "RS256" for OIDC
