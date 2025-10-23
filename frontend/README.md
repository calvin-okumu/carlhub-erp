# DjangoCRM Frontend

A modern Next.js frontend for the DjangoCRM multi-tenant Customer Relationship Management system.

## 🚀 Quick Start

### Automated Setup (Recommended)

Use the automated setup script for the fastest setup experience:

```bash
# Setup both backend and frontend
./setup.sh

# Or setup frontend only
./setup.sh --frontend-only

# Start development servers
make dev
```

The setup script will:
- ✅ Install dependencies
- ✅ Create environment configuration
- ✅ Run linting and type checking
- ✅ Validate setup

### Manual Setup

If you prefer manual control:

```bash
# Install dependencies
npm install

# Create environment file (copy from example)
cp .env.example .env.local

# Edit environment variables
# NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
# NEXT_PUBLIC_APP_ENV=development

# Start development server
npm run dev
```

## 🛠️ Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint

# Setup & Automation
npm run setup        # Run automated setup
npm run setup:ci     # CI environment setup
npm run setup:production  # Production setup
```

## 🏗️ Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── app/               # Next.js app router
│   │   ├── api/          # API routes (if needed)
│   │   ├── dashboard/    # Main application pages
│   │   ├── login/        # Authentication pages
│   │   └── signup/       # Registration pages
│   ├── components/       # Reusable React components
│   │   ├── dashboard/    # Dashboard-specific components
│   │   └── website/      # Landing page components
│   ├── hooks/           # Custom React hooks
│   └── api/             # API client functions
├── scripts/              # Automation scripts
│   └── setup.js         # Frontend setup automation
├── Dockerfile           # Docker containerization
└── next.config.ts       # Next.js configuration
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file with the following variables:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Production Settings (uncomment for production)
# NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
# NEXT_PUBLIC_APP_ENV=production
# NEXT_PUBLIC_SITE_URL=https://your-frontend-domain.com
```

### API Integration

The frontend communicates with the Django backend through:

- **REST API**: Direct HTTP calls to backend endpoints
- **Environment-based URLs**: Configurable API base URL
- **Development Proxy**: Next.js rewrites for local development

## 🐳 Docker Deployment

### Build and Run

```bash
# Build Docker image
docker build -t djangocrm-frontend .

# Run container
docker run -p 3000:3000 djangocrm-frontend
```

### Docker Compose

The frontend is included in the root `docker-compose.yml`:

```bash
# Start all services
docker-compose up -d

# Frontend available at: http://localhost:3000
```

## 🧪 Testing & Quality

### Automated Quality Checks

The setup script runs:
- ✅ **ESLint**: Code linting and style enforcement
- ✅ **TypeScript**: Type checking and compilation
- ✅ **Build Validation**: Ensures production build works

### Manual Testing

```bash
# Run linting
npm run lint

# Type checking
npx tsc --noEmit

# Build verification
npm run build
```

## 🚀 Deployment

### Development
```bash
npm run dev
# Available at: http://localhost:3000
```

### Production
```bash
npm run build
npm run start
# Or use Docker deployment
```

### CI/CD Integration

The frontend is fully integrated with GitHub Actions:

- **Automated Testing**: Runs on every push/PR
- **Build Verification**: Ensures production builds work
- **Docker Images**: Built and pushed automatically
- **Quality Gates**: Linting and type checking required

## 🔗 Integration with Backend

### API Communication

- **Base URL**: Configurable via `NEXT_PUBLIC_API_URL`
- **Authentication**: Token-based auth with backend
- **Error Handling**: Comprehensive error management
- **Loading States**: User-friendly loading indicators

### Development Workflow

1. **Backend First**: Start Django backend (`make dev-backend`)
2. **Frontend Second**: Start Next.js frontend (`make dev-frontend`)
3. **API Proxy**: Frontend proxies API calls to backend
4. **Hot Reload**: Both frontend and backend support hot reloading

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://reactjs.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

## 🤝 Contributing

1. Follow the automated setup process
2. Run quality checks before committing
3. Ensure TypeScript types are correct
4. Test API integration thoroughly

## 📄 License

This project is part of the DjangoCRM system. See the main project for licensing information.

## Test Workflow

This is a test change to trigger the CI/CD workflow on push to dev.
