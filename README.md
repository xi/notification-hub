# Notification Hub

Distraction-free notification daemon for linux inspired by github.

-	Notifications are never displayed directly on screen to avoid distraction.
-	If there are notifications, a status indicator is displayed. Clicking on that
	indicator reveals the current notifications in a menu.
-	Notifications are grouped by application. Only the latest notification for
	each application is shown.
-	Clicking on a notification removes it from the menu.

## Dependencies

-	[python3-gi](https://docs.gtk.org/gio/)
-	gir1.2-gtk-3.0
-	[gir1.2-ayatanaappindicator3-0.1](https://lazka.github.io/pgi-docs/AyatanaAppIndicator3-0.1/classes/Indicator.html)

## Known Limitations

-	Only supports `app_name`, `replaces_id`, and `summary`. Everything else
	(expiration, icons, HTML body, actions) is ignored.
-	Lies about the supported features to other software to avoid fallbacks (e.g.
	in firefox)
-	Does not display the summary of the previous notification if the latest one is
	closed.
-	Applications rarely close notifications that are no longer relevant (e.g.
	because you have just looked at the your new messages). So you have to close
	them manually.

## Background

I hate notifications. They are totally distracting and sometimes even leak
private information when they display the entirety of a private message while
someone else is looking at my screen.

Status indicators on the other hand are great. Tiny bits of information that I
can access at any time. Am I connected to the network? Are my speakers muted?
What is my current keyboard layout? Do I have unread messages? So easy to see
and completely non-distracting. A changing status indicator is just subtle
enough to be noticeable while staying out of the way.

Unfortunately, while the linux world has pretty much settled on a [standard for
notifications](https://developer.gnome.org/notification-spec/), status
indicators are in peril:

X11 protocols such as
[`_NET_WM_STATE_DEMANDS_ATTENTION`](https://specifications.freedesktop.org/wm-spec/wm-spec-latest.html)
and [system
tray](https://specifications.freedesktop.org/systemtray-spec/systemtray-spec-latest.html)
have been out of fashion for a while, but wayland will probably be the final
blow. Ubuntu toyed with something called [app
indicators](https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationIndicators)
for a while which was picked up by KDE and is now called
[StatusNotifierItem](https://freedesktop.org/wiki/Specifications/StatusNotifierItem/).
The original GTK implementation is now maintained by a small team under the name
of [AyatanaAppIndicator](https://sunweavers.net/blog/node/67). Gnome on the
other hand decided to [ditch status indicators
completly](https://blogs.gnome.org/aday/2017/08/31/status-icons-and-gnome/). In
their official documentation they even suggest to use notifications instead of
status indicators. Preposterous!

Irony aside, I can understand much of the criticism towards both the old system
tray and status indicators in general. I also agree that there are many cases
where status indicators are not the right tool and something else should be used
instead. But still, for some cases they are just perfect.

What ever the reasons, we now have a situation where application authors have no
clear guidance on how to implement status indicators and therefore don't do it.
So if you disable notifications (because you hate them) and a chat program has
no status indicator, there is just no way to get notified of new messages.

The silver lining here is that notifications and status are somewhat related.
For example, you can have a status indicator that only displays whether there
are any new notifications. This project is an experiment around exactly that
idea.

## Similar projects

-	[Rofication](https://github.com/DaveDavenport/Rofication) has similar goals
	but does not use StatusNotifierItem
