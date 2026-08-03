🔒 Fix insecure password exposure in UI configuration

🎯 **What:** The `password` field inside `Obico-HA-addon/config.json` was missing the `"secret": true` configuration property, causing the Home Assistant Add-on frontend UI to render it in plaintext.

⚠️ **Risk:** Storing or displaying passwords in plaintext within the addon configuration interface could lead to unauthorized exposure (e.g. shoulder surfing, screen grabs).

🛡️ **Solution:** Appended `"secret": true` to the schema properties for the `password` field. This directs the Home Assistant Supervisor to mask the input field on the addon's configuration tab, preventing unintended plaintext disclosure while preserving user-defined addon titles and formatting.
