# Logo Images

Place the WhatIDid.ai logo image in this directory:

## Required Image

**logo-icon.png** - Beaver mascot icon
- Used in: Website header (large, prominent display)
- Recommended size: 512x512px or higher, transparent background (PNG format)
- The image will be displayed at 80x80px in the header

## Current Status

⚠️ **Placeholder** - Please upload the beaver mascot logo to this directory as `logo-icon.png`.

## Usage

The logo is referenced in the base template (`templates/base.html`) with:
```html
<img src="{{ url_for('static', filename='img/logo-icon.png') }}" alt="WhatIDid.ai Beaver">
```

If the logo file is missing, the header will gracefully fall back to showing just the text "WhatIDid.ai".
