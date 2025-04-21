# Deploying to Netlify

## Prerequisites
- A Netlify account (free tier is sufficient)
- Netlify CLI installed (`npm install -g netlify-cli`)
- Git installed on your computer

## Deployment Steps

1. Create a new Git repository with the contents of this directory:
   ```
   cd magic-wheels-dashboard
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Login to Netlify CLI:
   ```
   netlify login
   ```

3. Initialize Netlify site:
   ```
   netlify init
   ```
   - Select "Create & configure a new site"
   - Follow the prompts to set up your site

4. Deploy to Netlify:
   ```
   netlify deploy --prod
   ```

5. Once deployment is complete, your dashboard will be available at the URL provided by Netlify

6. The first time you access the dashboard, you'll need to complete the OAuth flow:
   - Click the authorization link
   - Log in to your GoHighLevel account
   - Authorize the application
   - You'll be redirected back to the dashboard

## Updating the Dashboard

To update the dashboard in the future:
1. Make your changes
2. Commit them to Git
3. Run `netlify deploy --prod`

## Monitoring and Logs

- View logs and monitor performance in the Netlify dashboard
- Set up notifications for deploy events
