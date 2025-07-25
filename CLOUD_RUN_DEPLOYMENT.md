# Google Cloud Run Deployment Guide
# Complete setup for webhook-based Telegram bot deployment

## 🚀 **Complete Google Cloud Run Setup**

This guide provides **production-ready deployment** using Google Cloud Build triggers connected to your GitHub repository.

---

## **📋 Prerequisites**

1. **Google Cloud Project** with billing enabled
2. **GitHub Repository** with your bot code
3. **Telegram Bot Token** from @BotFather

---

## **⚙️ Step 1: Google Cloud Setup**

### Enable Required APIs
```bash
# Enable necessary Google Cloud APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Create Service Account
```bash
# Create service account for Cloud Run
gcloud iam service-accounts create cloud-run-service \
    --display-name="Cloud Run Service Account"

# Add required permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:cloud-run-service@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:cloud-run-service@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

### Store Bot Token Securely
```bash
# Create secret for bot token
echo "YOUR_BOT_TOKEN_HERE" | gcloud secrets create telegram-bot-token --data-file=-

# Verify secret creation
gcloud secrets list
```

---

## **🔗 Step 2: Connect GitHub to Cloud Build**

### Method 1: Google Cloud Console (Recommended)
1. Go to **Cloud Build → Triggers**
2. Click **"Create Trigger"**
3. Select **"GitHub (Cloud Build GitHub App)"**
4. **Connect your repository**
5. Configure trigger:
   - **Name**: `telegram-bot-deploy`
   - **Event**: Push to branch
   - **Branch**: `^main$`
   - **Configuration**: Cloud Build configuration file
   - **File location**: `cloudbuild.yaml`

### Method 2: Command Line
```bash
# Connect repository (interactive)
gcloud builds triggers create github \
    --repo-name=fileExtensionsChangerForTelegram \
    --repo-owner=kalashagnihotri \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --description="Deploy Telegram bot to Cloud Run"
```

---

## **📁 Step 3: Repository Structure**

Ensure your GitHub repository has these files:
```
📁 your-repo/
├── main.py                 # ✅ Webhook-based Flask app
├── requirements.txt        # ✅ Dependencies with Flask
├── Dockerfile             # ✅ Python 3.10 container
├── cloudbuild.yaml        # ✅ Build configuration
├── config/                 # Bot configuration
├── operations/             # File conversion operations
├── utils/                  # Utility functions
└── README.md              # Documentation
```

---

## **🚀 Step 4: Deploy**

### Automatic Deployment
```bash
# Push to main branch triggers automatic deployment
git add .
git commit -m "Deploy to Cloud Run with webhook support"
git push origin main
```

### Manual Deployment (if needed)
```bash
# Trigger build manually
gcloud builds submit --config=cloudbuild.yaml .
```

---

## **📞 Step 5: Set Telegram Webhook**

### Automatic Setup (Done by Cloud Build)
The `cloudbuild.yaml` automatically sets the webhook after deployment.

### Manual Setup (if needed)
```bash
# Get your Cloud Run service URL
SERVICE_URL=$(gcloud run services describe telegram-file-converter \
  --region=asia-south1 \
  --format="value(status.url)")

# Set webhook manually
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=${SERVICE_URL}/webhook" \
  -d "drop_pending_updates=true"

# Verify webhook
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

---

## **✅ Step 6: Verify Deployment**

### Health Check
```bash
# Test health endpoint
SERVICE_URL=$(gcloud run services describe telegram-file-converter \
  --region=asia-south1 \
  --format="value(status.url)")

curl "${SERVICE_URL}/health"
```

### Expected Response
```json
{
  "status": "healthy",
  "bot_username": "your_bot_username",
  "operations_available": {
    "images": true,
    "pdf": true,
    "videos": true
  },
  "timestamp": "2025-01-20T10:30:00"
}
```

### Test Bot
1. Open Telegram
2. Send `/start` to your bot
3. Upload a test image
4. Select a conversion operation
5. Verify converted file is returned

---

## **📊 Step 7: Monitor Deployment**

### View Logs
```bash
# Real-time logs
gcloud run logs tail telegram-file-converter --region=asia-south1 --follow

# Recent logs
gcloud run logs read telegram-file-converter --region=asia-south1 --limit=50
```

### Monitor Build Status
```bash
# List recent builds
gcloud builds list --limit=10

# Get build details
gcloud builds describe BUILD_ID
```

### Service Status
```bash
# Service information
gcloud run services describe telegram-file-converter --region=asia-south1

# Service metrics
gcloud run services list --platform=managed
```

---

## **🔧 Advanced Configuration**

### Resource Scaling
Edit `cloudbuild.yaml` to adjust:
```yaml
- '--memory=2Gi'          # RAM allocation
- '--cpu=2'               # CPU allocation  
- '--min-instances=0'     # Minimum instances
- '--max-instances=10'    # Maximum instances
```

### Environment Variables
Add custom environment variables:
```yaml
- '--set-env-vars=CUSTOM_VAR=value,ANOTHER_VAR=value'
```

### Custom Domain
```bash
# Map custom domain
gcloud run domain-mappings create \
  --service=telegram-file-converter \
  --domain=bot.yourdomain.com \
  --region=asia-south1
```

---

## **🛡️ Security Best Practices**

### Secret Management
- ✅ Bot token stored in Secret Manager
- ✅ Service account with minimal permissions
- ✅ No sensitive data in code or environment variables

### Network Security
- ✅ HTTPS-only communication
- ✅ Webhook signature validation
- ✅ Request rate limiting

### Container Security
- ✅ Non-root user in container
- ✅ Minimal base image (Python slim)
- ✅ Regular dependency updates

---

## **🚨 Troubleshooting**

### Common Issues

**Build Failed:**
```bash
# Check build logs
gcloud builds log BUILD_ID

# Common fixes:
# - Verify Dockerfile syntax
# - Check requirements.txt dependencies
# - Ensure all files are committed to GitHub
```

**Deployment Failed:**
```bash
# Check Cloud Run logs
gcloud run logs read telegram-file-converter --region=asia-south1

# Common fixes:
# - Verify bot token in Secret Manager
# - Check service account permissions
# - Validate port 8080 binding
```

**Webhook Not Working:**
```bash
# Check webhook status
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"

# Reset webhook
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/deleteWebhook"
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -d "url=https://your-service-url/webhook"
```

### Debug Commands
```bash
# Service logs with filtering
gcloud run logs read telegram-file-converter \
  --region=asia-south1 \
  --filter="severity>=ERROR"

# Container insights
gcloud run services describe telegram-file-converter \
  --region=asia-south1 \
  --format="table(metadata.name,status.url,status.conditions[0].type)"

# Build history
gcloud builds list \
  --filter="source.repoSource.repoName:fileExtensionsChangerForTelegram" \
  --limit=5
```

---

## **📈 Production Monitoring**

### Set Up Alerting
```bash
# Create alerting policy for errors
gcloud alpha monitoring policies create \
  --policy-from-file=alerting-policy.yaml
```

### Performance Monitoring
- Use **Google Cloud Monitoring** for metrics
- Set up **uptime checks** for health endpoint
- Monitor **request latency** and **error rates**
- Track **resource usage** (CPU, memory)

### Scaling Optimization
- Monitor **instance utilization**
- Adjust **min/max instances** based on usage
- Optimize **startup time** with container caching
- Use **traffic allocation** for gradual rollouts

---

## **🎯 What You Get**

✅ **Automated CI/CD** - Deploy on every GitHub push  
✅ **Webhook Architecture** - Efficient real-time processing  
✅ **Production Security** - Secret management & HTTPS  
✅ **Auto-scaling** - Handle traffic spikes automatically  
✅ **Monitoring** - Complete observability and alerting  
✅ **Zero Downtime** - Rolling deployments  

Your Telegram File Converter Bot is now **enterprise-ready** with Google Cloud Run! 🚀
