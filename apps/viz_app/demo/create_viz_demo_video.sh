#!/bin/bash
# Create Viz demo video from GIFs

set -e

VIZ_DIR="/home/ywatanabe/win/documents/SciTeX-Viz/templates/gif"
OUTPUT="static/videos/viz-demo.mp4"
TMP_DIR="tmp/viz_frames"

mkdir -p "$TMP_DIR"
mkdir -p static/videos

echo "Converting GIFs to frames..."

# Select key plot types for demo
GIFS=(
    "line-line"
    "scatter-scatter"
    "bar-bar"
    "violin-violin"
    "box-box"
    "heatmap"
    "polar-polar"
    "contour"
)

i=0
for gif_pattern in "${GIFS[@]}"; do
    gif_file=$(find "$VIZ_DIR" -name "${gif_pattern}*_cropped.gif" | head -1)
    if [ -f "$gif_file" ]; then
        # Extract first frame from GIF
        ffmpeg -i "$gif_file" -vframes 1 -y "$TMP_DIR/frame_$(printf "%03d" $i).png" 2> /dev/null
        echo "  ✓ $gif_pattern"
        ((i++))
    fi
done

echo "Creating video from frames..."
ffmpeg -framerate 1 -pattern_type glob -i "$TMP_DIR/frame_*.png" \
    -c:v libx264 -pix_fmt yuv420p -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" \
    -y "$OUTPUT" 2> /dev/null

# Cleanup
rm -rf "$TMP_DIR"

echo "✓ Viz demo video created: $OUTPUT"
ls -lh "$OUTPUT"
