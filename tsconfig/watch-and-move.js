#!/usr/bin/env node
/**
 * Watch mode companion - monitors .tsbuild and moves files on change
 *
 * Works alongside `tsc --watch` to automatically move compiled files
 * from ts/ to js/ directories in real-time
 */

const fs = require('fs');
const path = require('path');

const buildDir = path.join(__dirname, '..', '.tsbuild');
const targetDir = path.join(__dirname, '..');

console.log('👀 Watching build output for changes...');
console.log(`   Build dir: ${buildDir}`);

// Debounce helper
let timeout = null;
function debounce(fn, delay) {
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), delay);
    };
}

/**
 * Process all files in build directory
 */
function processFiles() {
    if (!fs.existsSync(buildDir)) {
        return;
    }

    let count = 0;

    function walk(dir) {
        const files = fs.readdirSync(dir);

        for (const file of files) {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);

            if (stat.isDirectory()) {
                walk(filePath);
            } else if (filePath.includes('/ts/') && /\.(js|js\.map|d\.ts|d\.ts\.map)$/.test(file)) {
                moveFile(filePath);
                count++;
            }
        }
    }

    walk(buildDir);

    if (count > 0) {
        console.log(`  ✓ Moved ${count} files`);
    }
}

/**
 * Move file from build dir to target dir
 */
function moveFile(srcPath) {
    const relativePath = path.relative(buildDir, srcPath);
    const targetPath = path.join(targetDir, relativePath.replace(/\/ts\//g, '/js/'));

    // Ensure target directory exists
    const targetDirPath = path.dirname(targetPath);
    if (!fs.existsSync(targetDirPath)) {
        fs.mkdirSync(targetDirPath, { recursive: true });
    }

    // Copy file
    try {
        fs.copyFileSync(srcPath, targetPath);
    } catch (err) {
        console.error(`  ✗ Failed to move ${relativePath}: ${err.message}`);
    }
}

// Initial processing
setTimeout(() => {
    console.log('📦 Processing initial files...');
    processFiles();
    console.log('✅ Ready - watching for changes');
}, 2000);

// Watch build directory
if (!fs.existsSync(buildDir)) {
    fs.mkdirSync(buildDir, { recursive: true });
}

const debouncedProcess = debounce(processFiles, 500);

fs.watch(buildDir, { recursive: true }, (eventType, filename) => {
    if (filename && /\.(js|js\.map|d\.ts|d\.ts\.map)$/.test(filename)) {
        console.log(`  📝 Change detected: ${filename}`);
        debouncedProcess();
    }
});

// Keep process alive
process.on('SIGINT', () => {
    console.log('\n👋 Stopping watch mode...');
    process.exit(0);
});
