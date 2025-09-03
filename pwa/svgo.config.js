/**
 * SVGO Configuration
 * 
 * Used by vite-plugin-imagemin during build
 * Can also be used standalone: npx svgo input.svg -o output.svg
 */

export default {
  multipass: true, // Run optimization multiple times for better results
  js2svg: {
    indent: 2, // Indentation for readability
    pretty: false, // Set to true for debugging
  },
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          // Don't minify IDs - keep them readable
          cleanupIds: {
            minify: false
          },
          
          // Remove default fill/stroke for better CSS control
          removeUnknownsAndDefaults: {
            keepDataAttrs: false,
            keepAriaAttrs: true,
            keepRoleAttrs: true
          },
          
          // Merge paths for smaller files
          mergePaths: {
            force: true
          }
        }
      }
    },
    
    // Control viewBox and dimensions separately
    {
      name: 'removeViewBox',
      active: false // Keep viewBox for responsive SVGs
    },
    {
      name: 'removeDimensions',
      active: false // Keep width/height attributes
    },
    
    // Remove unnecessary elements
    {
      name: 'removeComments',
      active: true
    },
    {
      name: 'removeMetadata',
      active: true
    },
    {
      name: 'removeXMLNS',
      active: false // Keep xmlns for standalone SVGs
    },
    
    // Optimize attributes
    {
      name: 'sortAttrs',
      active: true
    },
    {
      name: 'removeAttrs',
      params: {
        attrs: ['data-name'] // Remove common editor attributes
      }
    }
  ]
}