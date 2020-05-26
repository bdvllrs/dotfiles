EXT=HDMI2
INT=eDP1

xrandr | grep 'HDMI2 connected' && xrandr --output "${INT}" --auto --pos 0x2160 --scale 0.9999x0.9999 --primary --output "${EXT}" --auto --scale 1.9x1.9 --pos 0x0
xrandr | grep 'HDMI2 disconnected' && xrandr --output "${EXT}" --off

killall polybar; polybar -r default & polybar -r right
