# Setting Up OAuth for Production

## Overview
The Magic Wheels dashboard uses OAuth 2.0 to authenticate with the GoHighLevel API. When deploying to production, you need to update your OAuth application in GoHighLevel to use the production redirect URI.

## Steps to Update OAuth Configuration

1. **Log in to your GoHighLevel account**
   - Go to app.gohighlevel.com
   - Sign in with your agency credentials

2. **Navigate to your OAuth application**
   - Go to the same location where you created your OAuth application
   - Find the "Magic Wheels Dashboard" application

3. **Update the Redirect URI**
   - Edit the application settings
   - Update the Redirect URI to match your production URL:
     * For Render: https://magic-wheels-dashboard.onrender.com/callback
     * For Netlify: https://magic-wheels-dashboard.netlify.app/callback
     * For Vercel: https://magic-wheels-dashboard.vercel.app/callback
   - Save the changes

4. **Verify Environment Variables**
   - Make sure your production environment has these environment variables set:
     * GHL_CLIENT_ID: "68065d1e5068cea05378c233-m9r8sxby"
     * GHL_CLIENT_SECRET: "d0e56355-d952-473a-b4ec-3362904bed2a"
     * GHL_REDIRECT_URI: (The production callback URL from step 3)

## First-Time Authentication

The first time you access the dashboard in production, you'll need to complete the OAuth flow:

1. Visit your dashboard URL
2. You'll be prompted to authorize the application
3. Log in to GoHighLevel if needed
4. Approve the authorization request
5. You'll be redirected back to your dashboard

## Token Storage

In production, OAuth tokens are stored in a SQLite database in the data directory. This provides better security and persistence compared to file-based storage.

## Troubleshooting

If you encounter authentication issues:

1. Verify that the Redirect URI in GoHighLevel exactly matches your production callback URL
2. Check that environment variables are correctly set in your hosting platform
3. Look at the application logs for specific error messages
4. Try clearing the token by visiting /oauth/authorize to restart the authentication flow
