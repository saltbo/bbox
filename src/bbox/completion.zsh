# Native zsh completions for the commands installed by bbox.
# Load after compinit: source <(bbox completion zsh)

_bbox() {
    local -a versions options
    # Fire accepts named arguments before or after positionals. Offer their
    # names directly, then use _arguments for values and positional paths.
    if [[ "$PREFIX" == --* ]]; then
        case "$service" in
            charts-pull) options=('--help:Show help' '--since:Only download charts after this date' '--limit:Maximum number of charts') ;;
            docker-copy|nerdctl-copy) options=('--help:Show help' '--discard_ns:Drop the original image namespace' '--local:Skip pushing the copied image') ;;
        esac
        if (( $#options )); then
            _describe 'option' options
            return
        fi
    fi
    case "$service" in
        bbox)
            if (( CURRENT == 2 )); then
                _arguments '--help[Show help]' '--version[Show version]' '1:action:(completion)'
            elif [[ "$words[2]" == completion ]]; then
                _values 'shell' zsh
            fi
            ;;
        charts-pull)
            _arguments '--help[Show help]' '--since[Only download charts after this date]:date:' '--limit[Maximum number of charts]:count:' '1:repository URL:' '2:destination directory:_directories'
            ;;
        charts-push)
            _arguments '--help[Show help]' '1:chart directory:_directories' '2:repository:'
            ;;
        charts-mirror)
            _arguments '--help[Show help]' '1:mirror configuration:_files -g "*.yaml *.yml"'
            ;;
        docker-copy|nerdctl-copy)
            _arguments '--help[Show help]' '--discard_ns[Drop the original image namespace]:boolean:(True False)' '--local[Skip pushing the copied image]:boolean:(True False)' '1:source image:' '2:target registry:'
            ;;
        httptun)
            _arguments '--help[Show help]' '1:local port:' '2:subdomain:'
            ;;
        mkcourse)
            _arguments '--help[Show help]' '1:audio directory:_directories' '2:course name:' '3:introduction:' '4:author:'
            ;;
        git-cm)
            _arguments '1:commit type:(--feat --fix --docs --style --refactor --perf --build --ci --test --chore --revert)' '*:commit message:'
            ;;
        git-fire)
            _arguments '--help[Show help]' '-h[Show help]' '--version[Show version]' '-V[Show version]' '*:commit message:'
            ;;
        git-update-history-author)
            _arguments '1:old author email:'
            ;;
        kubectl-vsw)
            versions=("${XDG_DATA_HOME:-$HOME/.local/share}"/bbox/kubectl/kubectl*(N:t))
            versions=("${(@)versions#kubectl}")
            _describe 'cached Kubernetes version' versions
            ;;
        istioctl-vsw)
            versions=("${XDG_DATA_HOME:-$HOME/.local/share}"/bbox/istio/istio-*(N/:t))
            versions=("${(@)versions#istio-}")
            _describe 'cached Istio version' versions
            ;;
        ha-service-do)
            _arguments '1:entity ID:' '2:service:'
            ;;
        bark-notify)
            _arguments '1:notification title:' '2:notification message:'
            ;;
        buildctl|containerd|nerdctl|runc)
            # Reuse an upstream completion when one is already installed.
            local upstream="_$service"
            if (( $+functions[$upstream] )) || autoload -Uz +X "$upstream" 2>/dev/null; then
                "$upstream" "$@"
                return
            fi
            _files
            ;;
        *) return 1 ;;
    esac
}

# __BBOX_COMPDEF__
