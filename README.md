# Menu Judge

AI-powered menu analysis web application that decodes foreign restaurant menus instantly.

## Overview

Ever struggled to understand a menu while traveling abroad? Menu Judge solves this problem.

Simply snap a photo of any menu to get:
- **Dish translations** into English
- **Spiciness & sweetness levels** (1-5 scale)
- **Ingredients & allergen information**
- **Future**: Personalized dish recommendations based on your preferences

## Features

✨ **Instant Analysis** - AI-powered menu recognition using Claude Vision API
🌍 **Multi-language Support** - Analyzes menus in any language
📱 **Mobile-first Design** - Camera capture optimized for on-the-go use
🔒 **Privacy-focused** - API keys stored locally in browser, never sent to server
🎨 **Modern UI** - Beautiful dark mode interface with Tailwind CSS

## Tech Stack

- **Backend**: Python 3.13+, Flask
- **AI**: Claude API (Vision) by Anthropic
- **Frontend**: HTML/CSS/JavaScript
  - Tailwind CSS for styling
  - HTMX for dynamic updates
  - Alpine.js for interactivity
- **Architecture**: Multi-provider AI design (extensible to OpenAI, Gemini)

## Setup

### Prerequisites

- Python 3.13+
- Node.js 14+
- Anthropic API Key ([Get one here](https://console.anthropic.com/settings/keys))

### Installation

```bash
# Clone repository
git clone https://github.com/mitsumizo/menu-judge.git
cd menu-judge

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
npm install

# Build frontend assets
npm run build

# Set up environment variables
cp .env.example .env
# Edit .env file if needed (API key is entered via browser UI)

# Start development server
python run.py
```

### Development Build

When modifying frontend code:

```bash
# Rebuild CSS (Tailwind)
npm run build:css

# Recopy JS libraries
npm run build:js

# Build all assets
npm run build

# Watch CSS changes (auto-rebuild)
npm run watch:css
```

## Usage

1. Open `http://localhost:5000` in your browser
2. Enter your Anthropic API key in the settings modal
3. Upload or capture a menu image
4. View detailed analysis results

## Project Structure

```
menu-judge/
├── app/
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic (AI providers)
│   ├── models/          # Data models
│   ├── templates/       # Jinja2 templates
│   └── static/          # CSS, JS, images
├── tests/               # Unit tests
├── run.py              # Application entry point
└── requirements.txt    # Python dependencies
```

## Security

- API keys are stored in browser's `localStorage` and never transmitted to the server
- All API requests include the key in the `X-API-Key` header
- HTTPS recommended for production deployment

## Deployment

This application is designed for easy deployment to:
- **Render** (recommended)
- **Heroku**
- **Vercel**
- **Railway**
- **AWS EC2/ECS**

See [CLAUDE.md](./CLAUDE.md) for detailed deployment instructions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your portfolio or commercial applications.

## Acknowledgments

Built with [Claude Code](https://claude.com/claude-code) - AI-powered development assistant by Anthropic.
