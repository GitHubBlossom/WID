# Logo Images

Place the WhatIDid.ai logo images in this directory:

## Required Images

### 1. logo-icon.png - Beaver Mascot Icon
- **Used in**: Website header navigation (compact display)
- **Recommended size**: 512x512px or higher, transparent background (PNG format)
- **Display size**: 80x80px in the header
- **Referenced in**: `templates/base.html` and `templates/marketing_base.html`

### 2. logo-full.png - Full Beaver Mascot for Hero
- **Used in**: Marketing landing page hero section (large, prominent display)
- **Recommended size**: 800-1200px width, transparent background (PNG format)
- **Display size**: Up to 350px wide on desktop, 280px on mobile
- **Referenced in**: `templates/home.html`

## Current Status

⚠️ **Placeholder** - Please upload both beaver logos to this directory:
- `logo-icon.png` (smaller icon for header)
- `logo-full.png` (larger full logo for hero section)

## Usage

**Header Logo** (`templates/base.html` and `templates/marketing_base.html`):
```html
<img src="{{ url_for('static', filename='img/logo-icon.png') }}" alt="WhatIDid.ai Beaver">
```

**Hero Section Logo** (`templates/home.html`):
```html
<img src="{{ url_for('static', filename='img/logo-full.png') }}" alt="WhatIDid.ai Beaver Mascot">
```

Both images have graceful fallbacks - if the logo files are missing, they will be hidden and the text branding will be displayed instead.
