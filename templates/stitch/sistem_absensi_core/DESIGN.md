---
name: Sistem Absensi Core
colors:
  surface: '#0f1418'
  surface-dim: '#0f1418'
  surface-bright: '#343a3e'
  surface-container-lowest: '#0a0f12'
  surface-container-low: '#171c20'
  surface-container: '#1b2024'
  surface-container-high: '#252b2e'
  surface-container-highest: '#303539'
  on-surface: '#dee3e8'
  on-surface-variant: '#bdc8d1'
  inverse-surface: '#dee3e8'
  inverse-on-surface: '#2c3135'
  outline: '#87929a'
  outline-variant: '#3e484f'
  surface-tint: '#7bd0ff'
  primary: '#8ed5ff'
  on-primary: '#00354a'
  primary-container: '#38bdf8'
  on-primary-container: '#004965'
  inverse-primary: '#00668a'
  secondary: '#bcc7de'
  on-secondary: '#263143'
  secondary-container: '#3e495d'
  on-secondary-container: '#aeb9d0'
  tertiary: '#ffc176'
  on-tertiary: '#472a00'
  tertiary-container: '#f1a02b'
  on-tertiary-container: '#613b00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#c4e7ff'
  primary-fixed-dim: '#7bd0ff'
  on-primary-fixed: '#001e2c'
  on-primary-fixed-variant: '#004c69'
  secondary-fixed: '#d8e3fb'
  secondary-fixed-dim: '#bcc7de'
  on-secondary-fixed: '#111c2d'
  on-secondary-fixed-variant: '#3c475a'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb960'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f1418'
  on-background: '#dee3e8'
  surface-variant: '#303539'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  title-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  display-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-margin: 24px
  gutter: 16px
  section-gap: 32px
  card-padding: 20px
  sidebar-width: 260px
---

## Brand & Style

The design system is engineered for high-stakes administrative environments where speed of recognition and data clarity are paramount. It adopts a **Modern Corporate** aesthetic with a lean toward **Technical Minimalism**, prioritizing high-contrast legibility against a deep, non-distracting background.

The visual narrative focuses on security, precision, and efficiency. By utilizing a dark navy foundation paired with vibrant sky-blue accents, the system evokes a sense of advanced technology and reliability. The interface avoids unnecessary decorative elements, instead using structural alignment and purposeful color-coding to guide the administrator’s eye to critical attendance anomalies or system alerts.

## Colors

The color palette is optimized for long-duration monitoring. The primary background uses a deep navy to reduce eye strain, while the surface color provides a subtle lift for administrative cards.

- **Primary (#38bdf8):** Reserved for actionable items, active states, and successful facial matches.
- **Semantic Palette:** Success, Warning, and Danger colors are used strictly for status indicators (e.g., "Present," "Late," "Unauthorized Access").
- **Neutral Hierarchy:** Pure white is used for primary headings and data points. Light gray (#94a3b8) is utilized for secondary metadata and labels to create clear information depth.
- **Borders:** A consistent slate border (#334155) is used to define container boundaries without creating visual noise.

## Typography

This design system utilizes **Inter** for its exceptional legibility in data-heavy dashboards. The type scale is built on a modular rhythm to ensure that numerical data (attendance counts, timestamps) stands out clearly against descriptive text.

- **Headlines:** Use semi-bold weights with slight negative letter-spacing for a modern, compact feel.
- **Data Points:** Critical numbers in dashboard widgets should use the `display-lg` token to ensure immediate visibility.
- **Labels:** Small caps are used for table headers and secondary category labels to provide distinction from body data.

## Layout & Spacing

The layout follows a **Fluid Grid** model with a fixed sidebar for primary navigation. 

- **Sidebar:** Positioned on the left, it remains fixed at 260px to provide a persistent anchor for the administrator.
- **Main Content:** Utilizes a 12-column grid. Large data visualizations (Daily Attendance Trends) should span 8-12 columns, while smaller metric cards (Present Today, Late Arrivals) should span 3-4 columns.
- **Breakpoints:** On tablet devices, the sidebar collapses into a hamburger menu. On mobile, the 12-column grid reflows into a single-column stack with horizontal margins reduced to 16px.

## Elevation & Depth

In this design system, depth is communicated through **Tonal Layering** rather than heavy shadows. 

1. **Level 0 (Background):** The base Dark Navy (#0f172a).
2. **Level 1 (Cards/Sidebar):** Deep Slate (#1e293b) with a 1px solid border (#334155).
3. **Level 2 (Modals/Popovers):** A slightly lighter slate with a soft ambient shadow (0px 10px 15px -3px rgba(0,0,0,0.5)) to indicate focus.

Glassmorphism is used sparingly—only for the sidebar background and top navigation bar—utilizing a 12px backdrop blur to maintain context of the underlying data while scrolling.

## Shapes

The shape language is consistently "Rounded" to soften the technical nature of the system while maintaining a professional look.

- **Containers:** All dashboard cards, input fields, and main containers use a 12px (0.75rem) border radius.
- **Interaction Elements:** Buttons and tags use the same 12px radius, ensuring a unified visual rhythm. 
- **Icons:** Should follow a 2px stroke weight with slightly rounded terminals to match the container radius.

## Components

### Buttons
- **Primary:** Solid Sky Blue (#38bdf8) with black or very dark navy text. 
- **Ghost:** Transparent background with a Sky Blue border for secondary actions.

### Status Badges
- **Solid Variant:** Used for high-priority alerts (e.g., "Access Denied"). Uses high-saturation background with white text.
- **Soft Variant:** Used for standard table rows. Uses a 15% opacity version of the semantic color for the background, and the 100% opacity color for the text (e.g., Soft Green background with Emerald Green text for "Present").

### Progress Bars
- **Track:** Deep Slate (#1e293b).
- **Indicator:** Horizontal bars using a solid fill (Primary or Success). For multi-segment bars, use different shades of the primary color to show distribution (e.g., On-time vs. Excused).

### Sidebar Navigation
- **Default State:** Light Gray text, no background.
- **Active State:** Sky Blue text with a subtle left-aligned vertical "accent" bar (4px width) and a 5% opacity primary color background hover effect.

### Input Fields
- Dark Navy background (inset look) with a 1px Slate border. On focus, the border transitions to Sky Blue with a 2px outer glow.

### Cards
- Deep Slate background, 1px #334155 border, 20px internal padding. Title and "View More" actions should be aligned to the top-right header area within the card.