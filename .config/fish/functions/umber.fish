function umber --description "Switch the Ghostty Umber variant: auto or day"
    set -l config ~/.config/ghostty/config

    set -l value
    set -l label
    switch "$argv[1]"
        case auto ""
            set value 'dark:umber,light:umber-light'
            set label "auto (follows macOS appearance)"
        case day
            set value umber
            set label day
        case '*'
            echo "usage: umber [auto|day]" >&2
            return 1
    end

    if not test -f $config
        echo "umber: $config not found" >&2
        return 1
    end
    # Resolve first, so the rename below replaces the file a symlink points at
    # rather than the symlink itself.
    set config (path resolve $config)

    # Ghostty accepts any spacing around '=', and when a key repeats the last
    # one wins, so match loosely and rewrite every occurrence. Anchoring on
    # '^theme = ' would miss 'theme=umber' entirely and could leave a second
    # line that silently overrides the one we just changed.
    set -l pattern '^[[:blank:]]*theme[[:blank:]]*=.*$'
    if not grep -Eq $pattern $config
        echo "umber: no 'theme =' line in $config" >&2
        return 1
    end

    # Write a sibling temp file and rename it over the target: rename is atomic,
    # so an interrupted or failed run can never leave a truncated config. A
    # redirect straight onto $config would truncate first, and `cat >$config`
    # with an unset $tmp would then read stdin — destroying the file and hanging
    # the shell. $tmp is therefore checked explicitly rather than trusting the
    # exit status: `if not CMD` does not invert when CMD fails to start.
    set -l tmp (mktemp "$config.umber.XXXXXX")
    if test -z "$tmp" -o ! -f "$tmp"
        echo "umber: could not create a temp file beside $config" >&2
        return 1
    end

    sed -E "s|$pattern|theme = $value|" $config >$tmp
    set -l sed_status $status
    if test $sed_status -ne 0 -o ! -s "$tmp"
        rm -f $tmp
        echo "umber: could not rewrite $config" >&2
        return 1
    end

    if not grep -Eq "^theme = "(string escape --style=regex $value)'$' $tmp
        rm -f $tmp
        echo "umber: rewrite did not take effect" >&2
        return 1
    end

    # mktemp creates 0600, and the rename would carry that onto the config.
    # BSD stat first, then GNU: with coreutils on PATH, `stat -f` means
    # --file-system and prints a report instead of a mode, so the result is
    # validated rather than passed straight to chmod.
    set -l mode (stat -f '%Lp' $config 2>/dev/null)
    if not string match -qr '^[0-7]{3,4}$' -- "$mode"
        set mode (stat -c '%a' $config 2>/dev/null)
    end
    if not string match -qr '^[0-7]{3,4}$' -- "$mode"
        rm -f $tmp
        echo "umber: could not read the permissions of $config" >&2
        return 1
    end

    if not chmod $mode $tmp
        rm -f $tmp
        echo "umber: could not set permissions on the replacement for $config" >&2
        return 1
    end

    if not mv -f $tmp $config
        rm -f $tmp
        echo "umber: $config is not writable" >&2
        return 1
    end

    echo "Umber: $label"
    echo "Reload Ghostty with cmd+shift+, to apply."
end
