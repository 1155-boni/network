# Styling Instafinsta Project

## Current Work
Enhancing the visual design of the Instafinsta Django app to match an Instagram-inspired aesthetic: clean, minimal layout with black/white theme, rounded elements, subtle shadows, responsive design. This involves creating a custom CSS file and refactoring all templates to use consistent classes instead of inline styles.

## Key Technical Concepts
- Bootstrap 5 integration for base structure.
- Custom CSS (instafinsta.css) for theme: colors (#000, #fff, #fa, #e4405f accents), font-family: -apple-system, BlinkMacSystemFont, sans-serif.
- Responsive media queries for mobile/desktop.
- Classes like .instagram-card, .post-image, .follow-btn for consistency.

## Relevant Files and Code
- templates/base.html: Will link new CSS and refine sidebar.
- All templates: Remove inline styles, add custom classes.
- New: static/css/instafinsta.css.

## Problem Solving
- Current inline styles cause inconsistency; refactor to CSS classes.
- Ensure no breakage in functionality (e.g., AJAX scripts, forms).

## Pending Tasks and Next Steps
- [x] Create static/css/instafinsta.css with comprehensive Instagram-inspired styles (layout, cards, buttons, forms, posts, sidebar).
- [x] Update templates/base.html: Add link to instafinsta.css after Bootstrap; refine sidebar styles.
- [x] Refactor templates/login.html: Use .auth-card class for centered form, remove inline styles.
- [x] Refactor templates/signup.html: Similar to login, use consistent form styling.
- [x] Refactor templates/feed.html: Style posts as Instagram feed (rounded images, like/comment icons, gradient badges).
- [x] Refactor templates/profile.html: Profile card with avatar, bio, followers grid, posts in masonry layout.
- [x] Refactor templates/profile/view_profile.html: Update to match profile.html styling.
- [x] Refactor templates/create_post.html: Form with image preview, caption field like Instagram compose.
- [x] Refactor templates/explore.html: User grid with hover effects.
- [x] Refactor templates/messages/inbox.html: Chat bubbles, unread badges.
- [x] Refactor templates/messages/thread.html: Message thread styling.
- [x] Refactor templates/edit_profile.html: Form with profile pic upload preview.
- [x] Refactor templates/index.html: Landing page with hero or redirect styling.
- [ ] Test UI: Use browser_action to verify pages (login, feed, profile) load correctly and are responsive.
- [ ] Commit: "Add Instagram-inspired styling with custom CSS and template refactors".
