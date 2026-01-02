# ADvantage — Trend-Aware AI Ad Generator & Campaign Manager (Django)

ADvantage is a Django-based platform that generates **trend-aligned ad creatives** using an LLM and helps users run lightweight **email campaigns**. It collects **Google Trends (India, last 7 days)**, enriches each trend using **Google Custom Search**, summarizes it, stores it in **PostgreSQL**, and uses that context to create multiple ad options for a given product/description/tone. Users can pick/edit the best ad and send it to customers via **CSV upload** or **stored contacts**.

---

## Features

### Trend Pipeline
- Scrapes Google Trends (India, last 7 days) using **Selenium**
- Enriches trends with **Google Custom Search API**
- Generates short summaries with an LLM and stores them in **PostgreSQL**

### AI Ad Generation
- Generates multiple ad copies per request using trend summaries as context
- Supports tone selection (e.g., formal/casual/Gen-Z) and optional hashtags
- Allows selecting and editing the final ad before sending

### Campaign Distribution (Email)
- Sends the selected ad via email to:
  - a **CSV-uploaded customer list**, or
  - customers saved in the platform database
- Maintains basic email logs (success/failure)

### Customer Management
- Upload/import customers via **CSV/Excel**
- Stores reusable contact lists in the database

### Admin Utilities
- Admin login + trend refresh option
- Basic dashboard stats (usage + recent email logs)

---

## Tech Stack
- **Backend:** Django (Python)
- **Database:** PostgreSQL
- **AI:** OpenAI API (summaries + ad generation)
- **Trend Scraping:** Selenium + Chrome/ChromeDriver
- **Trend Enrichment:** Google Custom Search API
- **Email:** Django SMTP email backend

---

## Project Structure (High-Level)
