#!/usr/bin/env node

/**
 * 🔧 KRAI Setup Script
 * Comprehensive setup for development and production environments
 */

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const chalk = require('chalk');
const ora = require('ora');

async function main() {
    console.log(chalk.blue.bold(`
🤖 KRAI Setup Assistant
======================
`));

    // Check environment
    await checkEnvironment();
    
    // Test Supabase connection
    await testSupabaseConnection();
    
    // Setup development environment
    await setupDevelopment();
    
    console.log(chalk.green.bold('\n✅ KRAI Setup Complete!'));
    console.log(chalk.cyan(`
🚀 Next Steps:
- Run: ${chalk.yellow('npm run dev')} for development
- Run: ${chalk.yellow('npm run docker:up')} for Docker stack
- Visit: ${chalk.yellow('http://localhost:8000')} for admin dashboard
- API docs: ${chalk.yellow('http://localhost:8001/docs')}
`));
}

async function checkEnvironment() {
    const spinner = ora('Checking environment...').start();
    
    try {
        // Check required environment variables
        const required = ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'];
        const missing = required.filter(key => !process.env[key]);
        
        if (missing.length > 0) {
            spinner.fail(`Missing environment variables: ${missing.join(', ')}`);
            console.log(chalk.yellow('Please check your .env file'));
            process.exit(1);
        }
        
        // Check Node.js version
        const nodeVersion = process.version;
        const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
        
        if (majorVersion < 18) {
            spinner.warn(`Node.js ${nodeVersion} detected. Recommended: v18+`);
        }
        
        spinner.succeed('Environment check passed');
        
    } catch (error) {
        spinner.fail(`Environment check failed: ${error.message}`);
        process.exit(1);
    }
}

async function testSupabaseConnection() {
    const spinner = ora('Testing Supabase connection...').start();
    
    try {
        const supabase = createClient(
            process.env.SUPABASE_URL, 
            process.env.SUPABASE_SERVICE_KEY
        );
        
        // Test connection with a simple query
        const { data, error } = await supabase
            .from('manufacturers')
            .select('id')
            .limit(1);
        
        if (error) {
            spinner.fail(`Supabase connection failed: ${error.message}`);
            console.log(chalk.yellow('Please check your Supabase credentials'));
            process.exit(1);
        }
        
        spinner.succeed('Supabase connection successful');
        
    } catch (error) {
        spinner.fail(`Supabase test failed: ${error.message}`);
        process.exit(1);
    }
}

async function setupDevelopment() {
    const spinner = ora('Setting up development environment...').start();
    
    try {
        // Create necessary directories
        const dirs = [
            'uploads',
            'logs',
            'temp',
            'storage/app/public',
            'storage/logs'
        ];
        
        for (const dir of dirs) {
            const fullPath = path.join(__dirname, dir);
            if (!fs.existsSync(fullPath)) {
                fs.mkdirSync(fullPath, { recursive: true });
            }
        }
        
        // Copy environment files if they don't exist
        const envExample = path.join(__dirname, 'dashboard', '.env.example');
        const envFile = path.join(__dirname, 'dashboard', '.env');
        
        if (fs.existsSync(envExample) && !fs.existsSync(envFile)) {
            fs.copyFileSync(envExample, envFile);
        }
        
        spinner.succeed('Development environment ready');
        
    } catch (error) {
        spinner.fail(`Setup failed: ${error.message}`);
        process.exit(1);
    }
}

// Error handling
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    process.exit(1);
});

// Run setup
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { main, checkEnvironment, testSupabaseConnection };