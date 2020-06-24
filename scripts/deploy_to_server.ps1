git.exe push server
if (!$?) {
    exit 1
}
git.exe -C $(git remote get-url server) checkout $(git rev-parse HEAD)
if (!$?) {
    exit 1
}
Robocopy.exe lib\site-packages "$(git remote get-url server)\lib\site-packages" /MIR /R:0
if (!$?) {
    exit 1
}
