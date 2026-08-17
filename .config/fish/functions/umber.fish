function umber --description "Switch the Ghostty Umber variant: auto, day, or night"
    set -l config ~/.config/ghostty/config
    set -l mode $argv[1]
    switch "$mode"
        case auto ""
            set -l line 'theme = dark:umber,light:umber-light'
            sed -i '' "s|^theme = .*|$line|" $config
            echo "Umber: auto (follows macOS appearance)"
        case day
            sed -i '' 's|^theme = .*|theme = umber|' $config
            echo "Umber: day — 10.95:1 body text"
        case night
            sed -i '' 's|^theme = .*|theme = umber-night|' $config
            echo "Umber: night — 7:1 body text, 41% lower peak luminance"
        case '*'
            echo "usage: umber [auto|day|night]" >&2
            return 1
    end
    echo "Reload Ghostty with cmd+shift+, to apply."
end
