"""
Configuration file for GoHighLevel API connection
"""

# API credentials
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55X2lkIjoiOUpGaUVhYTAzdGhFaVFxRUI3WXoiLCJ2ZXJzaW9uIjoxLCJpYXQiOjE3NDUyNDQ1Mzk0MDMsInN1YiI6Ikk2aW81V0pFbTBZYjVtZFU3amhkIn0.TuUqfYM7nArxTzcyNq3-CKR9I16LLkkEanv68K9DMGc"

# Sub-accounts to track
SUB_ACCOUNTS = [
    "Magic Wheels Augusta",
    "Magic Wheels Columbus",
    "Magic Wheels Greenville",
    "Magic Wheels Jacksonville",
    "Magic Wheels Macon",
    "Magic Wheels Montgomery",
    "Magic Wheels Mobile",
    "Magic Wheels Pensacola",
    "Magic Wheels Savannah"
]

# Pipeline stages to track
PIPELINE_STAGES = [
    "Sold Retail",
    "Sold Rental"
]

# Update frequency (in seconds)
UPDATE_FREQUENCY = 3600  # Hourly updates initially

# Dashboard configuration
DASHBOARD_CONFIG = {
    "refresh_rate": "hourly",  # Will be changed to "daily" later
    "date_ranges": ["daily", "weekly", "monthly", "custom"],
    "default_date_range": "daily"
}
