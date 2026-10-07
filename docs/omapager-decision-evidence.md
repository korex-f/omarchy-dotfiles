# Omapager: read-only decision evidence

Inspected 2026-09-28. No reset, fetch, pull, commit, source modification or
notification-owner change was performed.

## Revisions and status

- Installed HEAD: `6fe51b5ea84a172bb43a26a6dee67bdd9bef9d87`, branch main.
- Remote: https://github.com/njpatel/omapager.git.
- Remote HEAD and refs/heads/main observed by git ls-remote:
  `c389e73516828d18f26e8efec2127c0c3dc3cb97`.
- Working tree: Widget.qml modified; +8/-12 lines.
- The remote commit was not fetched. No claim is made that the newest upstream
  code includes or supersedes the local patch.

## What would be lost by discarding the local change

At installed HEAD, primary click silences/re-enables notifications; right click
opens the options panel. The local modification makes every delivered click
open the panel and uses the panel's Notifications switch to silence/re-enable
notifications. It changes four tooltip expressions to describe that behavior.

Resetting Widget.qml to installed HEAD would lose the panel-on-primary-click
behavior and these tooltip corrections. It would restore click-to-silence and
right-click-for-options. Resetting to newest upstream would also change the
tracked source revision; its behavior has not been compared here. Neither
operation is authorized by this decision audit.

## Complete uncommitted diff

```diff
diff --git a/Widget.qml b/Widget.qml
index 4fe9c5d..22e7cb7 100644
--- a/Widget.qml
+++ b/Widget.qml
@@ -169,15 +169,11 @@ BarWidget {
     service.unsnooze(service.globalKey)
   }

-  // Left silences, right opens the panel. The fastest thing anyone wants from
-  // a notification indicator is for it to stop - and, once it has stopped, for
-  // it to start again - so that is the plain click; the panel is where you go
-  // to look at something rather than change it, which is what a right-click
-  // means everywhere else.
+  // Omarchy's bar currently forwards only primary-button clicks to user
+  // widgets. Open the options panel for that click, where its Notifications
+  // switch remains the explicit control for silencing and re-enabling alerts.
   function pressed(buttonCode) {
-    if (buttonCode === Qt.RightButton) togglePanel()
-    else if (quiet) letEverythingThrough()
-    else toggleSilence()
+    togglePanel()
   }

   // The system's own clock, not one hardcoded here: 24-hour on this desktop,
@@ -381,7 +377,7 @@ BarWidget {
       visible: pager.silenced
       text: pager.bellOff
       colour: pager.silencedColour
-      tooltipText: "Notifications silenced - click to allow them, right-click for options"
+      tooltipText: "Notification options - click to open"
     }

     Indicator {
@@ -390,11 +386,11 @@ BarWidget {
       colour: pager.snoozedColour
       tooltipText: pager.globalSnoozed
                    ? ("Everything snoozed, back " + pager.waking(pager.globalUntil)
-                      + " - right-click for options")
+                      + " - click for options")
                    : ((pager.snoozed.length === 1
                        ? (pager.snoozed[0].label + " snoozed " + pager.waking(pager.snoozed[0].until))
                        : (pager.snoozed.length + " sources snoozed"))
-                      + " - right-click for options")
+                      + " - click for options")
     }

     // The resting state, which only appears while the bar's inactive
@@ -405,7 +401,7 @@ BarWidget {
       text: pager.bellOff
       colour: pager.bar ? pager.bar.barForeground : Color.foreground
       quiet: true
-      tooltipText: "Silence notifications - right-click for options"
+      tooltipText: "Notification options - click to open"
     }
   }
```

## Notification ownership

Omapager Service.qml (lines 3-5 and 1427) creates a Quickshell
NotificationServer to own the session D-Bus name
`org.freedesktop.Notifications`. Stock Omarchy's
`shell/plugins/notifications/Service.qml` also creates NotificationServer
(line 931). These are competing notification servers, not complementary
widgets. Only one can own the well-known bus name.

Both services also register the shell IPC target `notifications`
(Omapager line 1633; stock service line 858). Omapager implements stock
dismiss/history/DND method names so existing stock shortcuts can keep working
with the stock service disabled. Activating both also creates an IPC target
collision; routing cannot be treated as a supported combination.

Live shell.json currently lists omarchy.notifications in disabledPlugins and
enables Omapager in plugins and the bar. This is configured ownership evidence,
not a runtime D-Bus probe. Stock plugin source remains installed and can remain
available as a fallback without running a second daemon.

Keeping all shipped plugins does not authorize silently enabling the stock
notification service alongside Omapager. The intended service owner and the
local patch's future canonical revision remain user decisions.

## Notification Center dependency

jankeesvw.notification-center is a history/archive widget, not a competing
NotificationServer. Its Panel.qml and helper watch stock notification JSON
under `~/.local/state/omarchy/notifications/`; its DND control resolves
`omarchy.notifications` or an enabled clone of that stock service.

Omapager instead stores its own history under
`~/.local/state/omarchy/omapager/`. Its compatibility IPC target does not make
it a clone or provide stock notification files. Notification Center therefore
cannot be assumed to receive new history or control DND with Omapager as owner.
Supporting both would need an explicit adapter or a choice of stock ownership.
Do not enable stock notifications just to satisfy the history widget.

Notification text, verification codes, pictures and histories are private
runtime state and stay outside dotfiles.
