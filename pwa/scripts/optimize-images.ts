#!/usr/bin/env tsx

/**
 * Image Optimization Script
 *
 * Optimizes all images in a directory using SVGO and Sharp
 * Usage: node scripts/optimize-images.js [directory]
 */

import fs from 'fs-extra'
import path from 'path'
import { fileURLToPath } from 'url'
import { optimize } from 'svgo'
import sharp from 'sharp'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, '..')

// Import SVGO config
const svgoConfig = await import(path.join(rootDir, 'svgo.config.js')).then(
  (m) => m.default
)

interface OptimizationResult {
  originalSize: number
  optimizedSize: number
  saved: number
  percent: string
}

async function optimizeSVG(filepath: string): Promise<OptimizationResult> {
  const input = await fs.readFile(filepath, 'utf8')
  const originalSize = Buffer.byteLength(input, 'utf8')

  const result = optimize(input, {
    path: filepath,
    ...svgoConfig,
  })

  const optimizedSize = Buffer.byteLength(result.data, 'utf8')
  const saved = originalSize - optimizedSize
  const percent = ((saved / originalSize) * 100).toFixed(1)

  await fs.writeFile(filepath, result.data)

  return {
    originalSize,
    optimizedSize,
    saved,
    percent,
  }
}

async function optimizeBitmap(filepath: string): Promise<OptimizationResult> {
  const ext = path.extname(filepath).toLowerCase()
  const originalStats = await fs.stat(filepath)
  const originalSize = originalStats.size

  let pipeline = sharp(filepath)

  switch (ext) {
    case '.jpg':
    case '.jpeg':
      pipeline = pipeline.jpeg({
        quality: 85,
        progressive: true,
        mozjpeg: true,
      })
      break

    case '.png':
      pipeline = pipeline.png({
        compressionLevel: 9,
        adaptiveFiltering: true,
      })
      break

    case '.webp':
      pipeline = pipeline.webp({
        quality: 85,
        effort: 6,
      })
      break

    default:
      throw new Error(`Unsupported image format: ${ext}`)
  }

  // Write to temp file first
  const tempPath = filepath + '.tmp'
  await pipeline.toFile(tempPath)

  const optimizedStats = await fs.stat(tempPath)
  const optimizedSize = optimizedStats.size

  // Only replace if smaller
  if (optimizedSize < originalSize) {
    await fs.rename(tempPath, filepath)
    const saved = originalSize - optimizedSize
    const percent = ((saved / originalSize) * 100).toFixed(1)

    return {
      originalSize,
      optimizedSize,
      saved,
      percent,
    }
  } else {
    await fs.remove(tempPath)
    return {
      originalSize,
      optimizedSize: originalSize,
      saved: 0,
      percent: '0',
    }
  }
}

async function optimizeImages(directory: string): Promise<void> {
  const dir = path.resolve(rootDir, directory)

  if (!(await fs.pathExists(dir))) {
    console.error(`❌ Directory not found: ${dir}`)
    process.exit(1)
  }

  console.log(`🖼️  Optimizing images in: ${directory}`)
  console.log('────────────────────────────────────────')

  const files = await fs.readdir(dir, { withFileTypes: true })
  const imageFiles = files
    .filter((f) => f.isFile())
    .filter((f) => /\.(svg|png|jpe?g|webp)$/i.test(f.name))
    .map((f) => path.join(dir, f.name))

  if (imageFiles.length === 0) {
    console.log('No image files found')
    return
  }

  let totalOriginal = 0
  let totalOptimized = 0

  for (const filepath of imageFiles) {
    const filename = path.basename(filepath)
    const ext = path.extname(filepath).toLowerCase()

    try {
      let result

      if (ext === '.svg') {
        result = await optimizeSVG(filepath)
      } else {
        result = await optimizeBitmap(filepath)
      }

      if (result && result.saved > 0) {
        console.log(
          `✅ ${filename}: ${formatSize(result.originalSize)} → ${formatSize(result.optimizedSize)} (-${result.percent}%)`
        )
        totalOriginal += result.originalSize
        totalOptimized += result.optimizedSize
      } else {
        console.log(`⚪ ${filename}: Already optimized`)
      }
    } catch (error) {
      console.error(
        `❌ ${filename}: ${error instanceof Error ? error.message : String(error)}`
      )
    }
  }

  if (totalOriginal > 0) {
    const totalSaved = totalOriginal - totalOptimized
    const totalPercent = ((totalSaved / totalOriginal) * 100).toFixed(1)

    console.log('────────────────────────────────────────')
    console.log(
      `📊 Total: ${formatSize(totalOriginal)} → ${formatSize(totalOptimized)} (-${totalPercent}%)`
    )
    console.log(`💾 Saved: ${formatSize(totalSaved)}`)
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
}

// Main
const directory = process.argv[2] || 'src/assets'

optimizeImages(directory).catch((error) => {
  console.error('❌ Optimization failed:', error)
  process.exit(1)
})
