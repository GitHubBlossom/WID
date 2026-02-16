# Logo Images

Place the WhatIDid.ai logo images in this directory:

## Required Images

1. **logo-full.png** - Full logo with "WhatIDid.ai - Your Week Summarized" text
   - Used in: Website header
   - Recommended size: Height 50-100px, transparent background

2. **logo-icon.png** - Beaver mascot icon (optional)
   - Used in: Favicon, mobile icons
   - Recommended size: 512x512px, transparent background

## Current Status

⚠️ **Placeholder** - Please upload the actual logo images to this directory.

## Usage

The logo is referenced in the base template (`templates/base.html`) with:
```html
<img src="{{ url_for('static', filename='img/logo-full.png') }}" alt="WhatIDid.ai" style="height: 50px;">
```

If the logo file is missing, the header will gracefully fall back to showing just the text "WhatIDid.ai".
