# SciTeX Video Assets

This directory contains video assets used in the SciTeX website.

## Current Videos

- **SciTeX-Demo-v01.mp4**: Main product demonstration video (5 min, 8x speed).

## Video Guidelines

When adding new videos to this directory, please follow these guidelines:

1. **Naming Convention**: Use descriptive names with version numbers (e.g., `ProductName-Purpose-v01.mp4`).

2. **Optimization**: Videos should be optimized for web delivery:
   - Use H.264 codec for maximum compatibility
   - Compress to a reasonable file size (aim for <100MB if possible)
   - Use appropriate resolution (720p or 1080p recommended)

3. **Documentation**: Update this README when adding new videos.

4. **Thumbnails**: Consider creating thumbnail images for video previews (e.g., `VideoName-thumb.jpg`).

## Implementation Notes

Videos are integrated into the site in the following locations:

- Landing page (`landing.html`) - Demo section with smaller embedded video
- Dedicated demo page (`demo.html`) - Full-featured video viewing experience
 
The embedded videos use the `preload="none"` attribute to prevent automatic downloading on page load, saving bandwidth for users who don't watch the videos.

## License Information

These videos are proprietary to SciTeX and should not be redistributed without permission.

---

*Last updated: May 21, 2025*