$ErrorActionPreference = "Stop"

function Invoke-NativeCommand {
    "+ $args"
    $command = $args[0]
    $arguments = $args[1..($args.Length)]
    & $command @arguments
    if (!$?) {
        Throw "exit code ${LastExitCode}: ${args}"
    }
}

Invoke-NativeCommand git fetch -f origin gh-pages
Invoke-NativeCommand git push -f server HEAD origin/gh-pages
Invoke-NativeCommand git -C $(git remote get-url server) checkout $(git rev-parse HEAD)
Invoke-NativeCommand git -C $(git remote get-url server) clean -fX *.pyc
Invoke-NativeCommand git -C "$(git remote get-url server)/docs/build/html" checkout $(git rev-parse origin/gh-pages)
Invoke-NativeCommand robocopy lib\site-packages "$(git remote get-url server)\lib\site-packages" /MIR /R:0
