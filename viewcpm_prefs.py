import json
import os

PREF_FILE = "viewcpm_prefs.json"

def load_prefs():
    """Load preferences from JSON file."""
    if os.path.exists(PREF_FILE):
        with open(PREF_FILE, "r") as f:
            return json.load(f)
    return {}

def save_prefs(prefs):
    """Save preferences to JSON file."""
    with open(PREF_FILE, "w") as f:
        json.dump(prefs, f, indent=2)

def get_pref(key, default=None):
    prefs = load_prefs()
    return prefs.get(key, default)

def set_pref(key, value):
    prefs = load_prefs()
    prefs[key] = value
    save_prefs(prefs)
