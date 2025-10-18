#!/bin/bash
# Create Viz demo video from GIFs in SciTeX-Viz directory
# Run from: /home/ywatanabe/win/documents/SciTeX-Viz/templates/gif

set -e

# Key plot GIFs to showcase
GIFS=(
  "line-line-line"
  "scatter-scatter"
  "bar-bar-bar"
  "violin-violin"
  "box-box-box"
  "heatmap"
  "polar-polar"
  "contour"
)

# Create temp directory
TMP_DIR="/home/ywatanabe/proj/scitex-cloud/tmp/viz_demo"
mkdir -p "$TMP_DIR"

echo "Extracting frames from GIFs..."
i=0
for pattern in "${GIFS[@]}"; do
  gif=$(ls ${pattern}*_cropped.gif 2>/dev/null | head -1)
  if [ -f "$gif" ]; then
    ffmpeg -i "$gif" -vframes 1 -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p" -y "$TMP_DIR/frame_$(printf '%03d' $i).png" 2>&1 | grep -v "^frame=\|^video:"
    echo "  ✓ $(basename $gif)"
    ((i++))
  fi
done

echo "Creating video..."
OUTPUT="/home/ywatanabe/proj/scitex-cloud/static/videos/viz-demo.mp4"
ffmpeg -framerate 1 -i "$TMP_DIR/frame_%03d.png" -c:v libx264 -pix_fmt yuv420p -y "$OUTPUT" 2>&1 | tail -3

echo "✓ Created: $OUTPUT"
ls -lh "$OUTPUT"

# Cleanup
rm -rf "$TMP_DIR"
