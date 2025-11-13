


# GFPS – Mobile App Guide

The mobile app is built with **React Native** and **Expo**, using **Expo Router** for navigation and **Contexts** for auth and coupon state.

---

## 1. Structure

```text
mobile/
  app/
    _layout.tsx         # App shell, wraps with providers
    index.tsx           # Dashboard
    login.tsx           # Google Sign-In
    fixtures.tsx        # Fixtures list
    match.tsx           # Markets and "Add to coupon"
    coupon.tsx          # Current coupon builder
    coupon-history.tsx  # Saved coupons
    favorites.tsx       # Favorite leagues
    profile.tsx         # Account / logout
    community.tsx       # Chat UI (skeleton)
    live.tsx            # Live screen (streamer)
    settings.tsx        # Placeholder for extra settings
    components/
      MatchCard.tsx
      MarketSelector.tsx
      CouponView.tsx
      TeamBadge.tsx

  auth/
    AuthContext.tsx

  notifications/
    registerPush.ts

  package.json
  app.json
  tsconfig.json
