export const FAVORITES_KEY = "dae-s10-favorites";

// localStorage can throw (private windows, blocked storage) or contain anything.
export function readFavorites() {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(FAVORITES_KEY));
    if (!Array.isArray(parsed)) {
      return [];
    }
    return [...new Set(parsed.filter((id) => Number.isInteger(id)))];
  } catch {
    return [];
  }
}

export function writeFavorites(favorites) {
  try {
    window.localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites));
  } catch {
    // Favorites are a convenience: the page still works without storage.
  }
}
