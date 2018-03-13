# kodi-repo

## Updating

1.  Update `default.py`
2.  Bump version number in `kodi-repo/repo/plugin.video.streamroyale/code/addon.xml`
3.  Zip `cd ~/projects/kodi-repo/repo/plugin.video.streamroyale && zip -r plugin.video.streamroyale-<new_version_number>.zip code/`
4.  update `addons.xml` to new version number
5.  run `cd ~/projects/kodi-repo/repo/ && md5 -q addons.xml|tr "\n" " " > addons.xml.md5`
6.  push it?
