#!/usr/bin/env node
/**
 * Post-build script to organize compiled JS files for Django static serving
 *
 * TypeScript compiles:
 *   apps/writer_app/static/writer_app/ts/index.ts
 * To:
 *   .tsbuild/apps/writer_app/static/writer_app/ts/index.js
 *
 * This script moves to:
 *   .jsbuild/writer_app/js/index.js
 *
 * Django serves from .jsbuild/ which is a Docker-only directory (not synced to host)
 * This keeps TS source as the only files on host, eliminating permission issues
 */

const fs = require('fs');
const path = require('path');

const buildDir = path.join(__dirname, '..', '.tsbuild');
const targetDir = path.join(__dirname, '..', '.jsbuild');

console.log('📦 Post-build: Moving compiled files to .jsbuild/ (Docker-only)...');

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
 * Move file from build dir to .jsbuild/, reorganizing path structure
 *
 * Input:  .tsbuild/apps/writer_app/static/writer_app/ts/index.js
 * Output: .jsbuild/writer_app/js/index.js
 *
 * Input:  .tsbuild/static/shared/ts/utils/index.js
 * Output: .jsbuild/shared/js/utils/index.js
 */
function moveFile(srcPath) {
    // Get path relative to build dir
    const relativePath = path.relative(buildDir, srcPath);

    let targetPath;

    // Handle app static files: apps/{app_name}/static/{app_name}/ts/...
    const appMatch = relativePath.match(/^apps\/([^\/]+)\/static\/([^\/]+)\/ts\/(.+)$/);
    if (appMatch) {
        const [, appName, staticName, rest] = appMatch;
        targetPath = path.join(targetDir, staticName, 'js', rest);
    }
    // Handle shared static files: static/shared/ts/...
    else if (relativePath.startsWith('static/shared/ts/')) {
        const rest = relativePath.replace('static/shared/ts/', '');
        targetPath = path.join(targetDir, 'shared', 'js', rest);
    }
    // Fallback: just replace /ts/ with /js/
    else {
        targetPath = path.join(targetDir, relativePath.replace(/\/ts\//g, '/js/'));
    }

    // Ensure target directory exists
    ensureDir(path.dirname(targetPath));

    // Copy file
    fs.copyFileSync(srcPath, targetPath);

    const displayPath = path.relative(targetDir, targetPath);
    console.log(`  ✓ ${displayPath}`);
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
