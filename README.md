# WhatsApp ChatGPT 3.5 Turbo with Flask

### Facebook WhatsApp Setup
1. https://developers.facebook.com/apps/
2. Create App
3. Go to created app, click Add products to your app, add WhatsApp

### Deploy Flask in Vercel or PythonAnywhere
- https://vercel.com/
- https://pythonanywhere.com/

### WA Webhook Setup
1. Whatsapp -> Configuration
2. Edit webhook's callback URL: 
  - Callback URL: url/receive_msg
  - Verify token: Is any string, defined in FACEBOOK_VERIFY_TOKEN
3. In page Getting started:
  - FACEBOOK_PHONE_NUMBER_ID = Phone number ID
  - FACEBOOK_VERSION = from the Send messages with the API curl (v15.0)
  - FACEBOOK_ACCESS_TOKEN = Temporary access token

