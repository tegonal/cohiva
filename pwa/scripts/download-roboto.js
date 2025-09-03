#!/usr/bin/env node

/**
 * Downloads Roboto font files from Google Fonts
 */

import fs from 'fs-extra'
import path from 'path'
import https from 'https'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, '..')

// Roboto font URLs for essential weights (Latin subset)
const fonts = [
  // Regular weights
  { weight: '300', style: 'normal', filename: 'roboto-v30-latin-300.woff2', 
    url: 'https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmSU5fBBc4.woff2' },
  { weight: '400', style: 'normal', filename: 'roboto-v30-latin-regular.woff2',
    url: 'https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2' },
  { weight: '500', style: 'normal', filename: 'roboto-v30-latin-500.woff2',
    url: 'https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmEU9fBBc4.woff2' },
  { weight: '700', style: 'normal', filename: 'roboto-v30-latin-700.woff2',
    url: 'https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmWUlfBBc4.woff2' },
  
  // Italic weights
  { weight: '300', style: 'italic', filename: 'roboto-v30-latin-300italic.woff2',
    url: 'https://fonts.gstatic.com/s/roboto/v30/KFOjCnqEu92Fr1Mu51TjASc6CsQ.woff2' },
  { weight: '400', style: 'italic', filename: 'roboto-v30-latin-italic.woff2',
    url: 'https://fonts.gstatic.com/s/roboto/v30/KFOkCnqEu92Fr1Mu51xIIzI.woff2' },
  { weight: '500', style: 'italic', filename: 'roboto-v30-latin-500italic.woff2',
    url: 'https://fonts.gstatic.com/s/roboto/v30/KFOjCnqEu92Fr1Mu51S7ACc6CsQ.woff2' },
  { weight: '700', style: 'italic', filename: 'roboto-v30-latin-700italic.woff2',
    url: 'https://fonts.gstatic.com/s/roboto/v30/KFOjCnqEu92Fr1Mu51TzBic6CsQ.woff2' }
]

async function downloadFile(url, filepath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filepath)
    
    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download ${url}: ${response.statusCode}`))
        return
      }
      
      response.pipe(file)
      
      file.on('finish', () => {
        file.close()
        resolve()
      })
      
      file.on('error', (err) => {
        fs.unlink(filepath, () => {}) // Delete incomplete file
        reject(err)
      })
    }).on('error', reject)
  })
}

async function downloadRobotoFonts() {
  const fontsDir = path.join(rootDir, 'config', 'fonts')
  
  console.log('📦 Downloading Roboto font files...')
  console.log(`   Target directory: ${fontsDir}`)
  
  // Ensure fonts directory exists
  await fs.ensureDir(fontsDir)
  
  // Download each font file
  for (const font of fonts) {
    const filepath = path.join(fontsDir, font.filename)
    
    try {
      console.log(`   Downloading ${font.filename}...`)
      await downloadFile(font.url, filepath)
      console.log(`   ✅ ${font.filename}`)
    } catch (error) {
      console.error(`   ❌ Failed to download ${font.filename}: ${error.message}`)
    }
  }
  
  console.log('✅ Roboto fonts downloaded successfully!')
}

// Run the download
downloadRobotoFonts().catch((error) => {
  console.error('❌ Download failed:', error)
  process.exit(1)
})