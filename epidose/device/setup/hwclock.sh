#!/bin/sh
# hwclock.sh	Set and adjust the controller clock.
#

### BEGIN INIT INFO
# Provides:          hwclock
# Required-Start:    mountdevsubfs
# Required-Stop:     mountdevsubfs
# Should-Stop:       umountfs
# Default-Start:     S
# X-Start-Before:    checkroot
# Default-Stop:      0 6
# Short-Description: Sync hardware and system clock time.
### END INIT INFO

# We only want to use the system timezone or else we'll get
# potential inconsistency at startup.
unset TZ

# Execute the device I/O Python script
device_io()
{
  /opt/venvs/epidose/bin/python3 /opt/venvs/epidose/lib/python3.7/site-packages/epidose/device/device_io.py "$@"
}

hwclocksh()
{
    . /lib/lsb/init-functions
    verbose_log_action_msg() { [ "$VERBOSE" = no ] || log_action_msg "$@"; }

    case "$1" in
	start)
            log_action_msg "Setting the system clock"
            date --set="$(device_io -c)"
            verbose_log_action_msg "System Clock set to: `date $UTC`"
	    ;;
	stop|restart|reload|force-reload)
            log_action_msg "Saving the system clock"
            device_io -C
            verbose_log_action_msg "Hardware Clock updated to `date`"
	    ;;
	show)
            device_io -c
	    ;;
	*)
	    log_success_msg "Usage: hwclock.sh {start|stop|reload|force-reload|show}"
	    log_success_msg "       start sets kernel (system) clock from hardware (RTC) clock"
	    log_success_msg "       stop and reload set hardware (RTC) clock from kernel (system) clock"
	    return 1
	    ;;
    esac
}

hwclocksh "$@"
