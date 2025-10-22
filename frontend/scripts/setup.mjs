#!/usr/bin/env node

/**
 * Frontend Setup Script
 * Automates frontend environment setup, dependency installation, and validation
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

class FrontendSetup {
  constructor() {
    this.rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
    this.isCI = process.env.CI || process.env.GITHUB_ACTIONS;
    this.isProduction = process.env.NODE_ENV === 'production' || process.argv.includes('--production');
    this.skipInstall = process.argv.includes('--skip-install');
    this.isCiMode = process.argv.includes('--ci');
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
    const colors = {
      info: '\x1b[36m',
      success: '\x1b[32m',
      warning: '\x1b[33m',
      error: '\x1b[31m',
      reset: '\x1b[0m'
    };
    console.log(`${colors[type]}[${timestamp}] ${message}${colors.reset}`);
  }

  detectEnvironment() {
    if (this.isCI || this.isCiMode) return 'ci';
    if (this.isProduction) return 'production';
    if (fs.existsSync(path.join(this.rootDir, '.git'))) return 'development';
    return 'staging';
  }

  runCommand(command, description, options = {}) {
    try {
      this.log(`🔄 ${description}...`, 'info');
      const result = execSync(command, {
        cwd: this.rootDir,
        stdio: options.silent ? 'pipe' : 'inherit',
        ...options
      });
      this.log(`✅ ${description} completed`, 'success');
      return result;
    } catch (error) {
      this.log(`❌ ${description} failed: ${error.message}`, 'error');
      throw error;
    }
  }

  installDependencies() {
    if (this.skipInstall) {
      this.log('⏭️  Skipping dependency installation', 'warning');
      return;
    }

    const packageManager = this.detectPackageManager();
    this.log(`📦 Using ${packageManager} for dependency installation`, 'info');

    if (packageManager === 'yarn') {
      this.runCommand('yarn install', 'Installing dependencies with Yarn');
    } else {
      this.runCommand('npm install', 'Installing dependencies with npm');
    }
  }

  detectPackageManager() {
    // Check for lock files to determine package manager
    if (fs.existsSync(path.join(this.rootDir, 'yarn.lock'))) return 'yarn';
    if (fs.existsSync(path.join(this.rootDir, 'pnpm-lock.yaml'))) return 'pnpm';
    if (fs.existsSync(path.join(this.rootDir, 'package-lock.json'))) return 'npm';
    return 'npm'; // default
  }

  createEnvironmentFile() {
    const envPath = path.join(this.rootDir, '.env.local');
    const envExamplePath = path.join(this.rootDir, '.env.example');

    // Create .env.example if it doesn't exist
    if (!fs.existsSync(envExamplePath)) {
      this.createEnvExample();
    }

    // Create .env.local for development if it doesn't exist
    if (!fs.existsSync(envPath) && this.detectEnvironment() === 'development') {
      this.log('📝 Creating .env.local for development', 'info');
      const envContent = `# Frontend Environment Configuration
# Copy from .env.example and update values for your environment

# API Configuration
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Add other environment variables as needed
`;
      fs.writeFileSync(envPath, envContent);
      this.log('✅ Created .env.local', 'success');
    } else if (fs.existsSync(envPath)) {
      this.log('ℹ️  .env.local already exists', 'info');
    }
  }

  createEnvExample() {
    const envExamplePath = path.join(this.rootDir, '.env.example');
    this.log('📝 Creating .env.example template', 'info');

    const envContent = `# Frontend Environment Configuration
# Copy this file to .env.local and update values for your environment

# API Configuration
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Production Settings (uncomment for production)
# NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
# NEXT_PUBLIC_APP_ENV=production
# NEXT_PUBLIC_SITE_URL=https://your-frontend-domain.com

# Add other environment variables as needed
`;
    fs.writeFileSync(envExamplePath, envContent);
    this.log('✅ Created .env.example', 'success');
  }

  validateSetup() {
    this.log('🔍 Validating frontend setup...', 'info');

    // Check if package.json exists
    if (!fs.existsSync(path.join(this.rootDir, 'package.json'))) {
      throw new Error('package.json not found');
    }
    this.log('✅ package.json found', 'success');

    // Check if node_modules exists (unless skipped)
    if (!this.skipInstall && !fs.existsSync(path.join(this.rootDir, 'node_modules'))) {
      throw new Error('node_modules not found - dependencies may not be installed');
    }
    if (!this.skipInstall) {
      this.log('✅ node_modules found', 'success');
    }

    // Check if Next.js config exists
    if (!fs.existsSync(path.join(this.rootDir, 'next.config.ts'))) {
      throw new Error('next.config.ts not found');
    }
    this.log('✅ Next.js configuration found', 'success');

    // Try to run a basic Next.js check
    try {
      this.runCommand('npx next --version', 'Checking Next.js version', { silent: true });
    } catch {
      this.log('⚠️  Could not verify Next.js version', 'warning');
    }
  }

  runLinting() {
    try {
      this.runCommand('npm run lint', 'Running ESLint');
    } catch {
      this.log('⚠️  Linting failed, but continuing setup', 'warning');
    }
  }

  runTypeCheck() {
    try {
      this.runCommand('npx tsc --noEmit', 'Running TypeScript type check');
    } catch {
      this.log('⚠️  Type checking failed, but continuing setup', 'warning');
    }
  }

  displaySuccessMessage(environment) {
    this.log('🎉 Frontend setup complete!', 'success');
    console.log('\nNext steps:');

    if (environment === 'development') {
      console.log('1. Configure API URL in .env.local if needed');
      console.log('2. Run: npm run dev');
      console.log('3. Open: http://localhost:3000');
    } else if (environment === 'production') {
      console.log('1. Configure production environment variables');
      console.log('2. Run: npm run build');
      console.log('3. Run: npm run start');
    } else {
      console.log('1. Configure environment-specific settings');
      console.log('2. Run: npm run dev');
    }

    console.log('');
  }

  async run() {
    try {
      const environment = this.detectEnvironment();
      this.log(`🚀 Starting Frontend Setup for ${environment} environment`, 'info');

      // Phase 1: Install dependencies
      this.installDependencies();

      // Phase 2: Create environment files
      this.createEnvironmentFile();

      // Phase 3: Validate setup
      this.validateSetup();

      // Phase 4: Run quality checks (skip in CI for speed)
      if (!this.isCI && !this.isCiMode) {
        this.runLinting();
        this.runTypeCheck();
      }

      this.displaySuccessMessage(environment);

    } catch (error) {
      this.log(`❌ Setup failed: ${error.message}`, 'error');
      process.exit(1);
    }
  }
}

// Run the setup if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const setup = new FrontendSetup();
  setup.run();
}

export default FrontendSetup;