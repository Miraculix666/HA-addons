🔒 [Security Fix] Remove hardcoded personal device entity_id

### 🎯 What
Removed the hardcoded personal device entity ID (`notify.mobile_app_marius_mi_15t_pro`) from the fallback action in the `universal_notification.yaml` blueprint.

### ⚠️ Risk
If left unfixed, this blueprint would inadvertently send notification data (which may contain sensitive information depending on the caller) to a specific, hardcoded personal device, regardless of who installed or used the blueprint.

### 🛡️ Solution
Removed the fallback action block completely. The preceding action already broadcasts to `notify.notify` (which targets all registered companion app devices) dynamically. Removing the hardcoded fallback prevents data leakage while preserving the intended generic notification functionality.
