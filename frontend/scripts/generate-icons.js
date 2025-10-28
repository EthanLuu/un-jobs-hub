/**
 * Generate all icon sizes from SVG
 *
 * Requirements:
 * - npm install sharp
 *
 * Usage:
 * - node scripts/generate-icons.js
 */

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const SVG_PATH = path.join(__dirname, '../public/icon.svg');
const PUBLIC_DIR = path.join(__dirname, '../public');

const ICON_SIZES = [
  { name: 'favicon-16x16.png', size: 16 },
  { name: 'favicon-32x32.png', size: 32 },
  { name: 'apple-touch-icon.png', size: 180 },
  { name: 'android-chrome-192x192.png', size: 192 },
  { name: 'android-chrome-512x512.png', size: 512 },
];

async function generateIcons() {
  console.log('📦 Generating icons from SVG...\n');

  try {
    // Read SVG file
    const svgBuffer = fs.readFileSync(SVG_PATH);

    // Generate each icon size
    for (const icon of ICON_SIZES) {
      const outputPath = path.join(PUBLIC_DIR, icon.name);

      await sharp(svgBuffer)
        .resize(icon.size, icon.size, {
          fit: 'contain',
          background: { r: 0, g: 0, b: 0, alpha: 0 }
        })
        .png()
        .toFile(outputPath);

      console.log(`✅ Generated: ${icon.name} (${icon.size}x${icon.size})`);
    }

    // Generate favicon.ico (multi-size)
    console.log('\n📦 Generating favicon.ico...');
    const favicon16 = await sharp(svgBuffer)
      .resize(16, 16)
      .png()
      .toBuffer();

    const favicon32 = await sharp(svgBuffer)
      .resize(32, 32)
      .png()
      .toBuffer();

    // Note: Sharp doesn't support ICO format directly
    // For production, use an online converter or ImageMagick
    console.log('⚠️  Note: favicon.ico needs to be generated manually');
    console.log('   Use: https://realfavicongenerator.net/');
    console.log('   Or: convert favicon-16x16.png favicon-32x32.png favicon.ico\n');

    console.log('✨ Icon generation complete!\n');
    console.log('📋 Generated files:');
    ICON_SIZES.forEach(icon => console.log(`   - ${icon.name}`));

    console.log('\n💡 Next steps:');
    console.log('   1. Generate favicon.ico manually (see above)');
    console.log('   2. Test icons: npm run dev');
    console.log('   3. Commit changes: git add public/ && git commit\n');

  } catch (error) {
    console.error('❌ Error generating icons:', error.message);
    process.exit(1);
  }
}

// Run the script
if (require.main === module) {
  generateIcons();
}

module.exports = { generateIcons };
