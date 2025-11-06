#!/usr/bin/env node
/**
 * Post-build script to move compiled JS files from ts/ to js/ directories
 *
 * TypeScript compiles:
 *   apps/writer_app/static/writer_app/ts/index.ts
 * To:
 *   .tsbuild/apps/writer_app/static/writer_app/ts/index.js
 *
 * This script moves to:
 *   apps/writer_app/static/writer_app/js/index.js
 */

const fs = require('fs');
const path = require('path');

const buildDir = path.join(__dirname, '..', '.tsbuild');
const targetDir = path.join(__dirname, '..');

console.log('📦 Post-build: Moving compiled files from ts/ to js/ directories...');

/**
 * Recursively find all files in a directory
 */
function findFiles(dir, pattern) {
    const results = [];

    if (!fs.existsSync(dir)) {
        return results;
    }

    const files = fs.readdirSync(dir);

    for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory()) {
            results.push(...findFiles(filePath, pattern));
        } else if (pattern.test(filePath)) {
            results.push(filePath);
        }
    }

    return results;
}

/**
 * Ensure directory exists
 */
function ensureDir(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

/**
 * Move file from build dir to target dir, changing ts/ to js/
 */
function moveFile(srcPath) {
    // Get path relative to build dir
    const relativePath = path.relative(buildDir, srcPath);

    // Replace /ts/ with /js/ in the path
    const targetPath = path.join(targetDir, relativePath.replace(/\/ts\//g, '/js/'));

    // Ensure target directory exists
    ensureDir(path.dirname(targetPath));

    // Copy file
    fs.copyFileSync(srcPath, targetPath);

    console.log(`  ✓ ${relativePath.replace(/\/ts\//g, '/js/')}`);
}

// Find all compiled files (.js, .js.map, .d.ts, .d.ts.map)
const patterns = [/\.js$/, /\.js\.map$/, /\.d\.ts$/, /\.d\.ts\.map$/];
let totalFiles = 0;

for (const pattern of patterns) {
    const files = findFiles(buildDir, pattern);

    for (const file of files) {
        // Only process files in ts/ directories
        if (file.includes('/ts/')) {
            moveFile(file);
            totalFiles++;
        }
    }
}

console.log(`✅ Moved ${totalFiles} files from ts/ to js/ directories`);

// Clean up build directory
console.log('🧹 Cleaning up build directory...');
if (fs.existsSync(buildDir)) {
    fs.rmSync(buildDir, { recursive: true, force: true });
    console.log('✅ Build directory cleaned');
}
