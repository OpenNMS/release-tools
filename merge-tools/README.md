After you do a release, the POMs in the latest `release-XX.x` branch will conflict with `develop` when they merge forward.

You can run this script to fix _most_ of them automatically.
For example, after release, and `<version>33.0.2</version>` entries turn to `<version>33.0.3-SNAPSHOT</version>` in the `release-33.x` branch, you can do the following to fix the merge failure:

```bash
git checkout develop
git pull
git merge origin/release-33.x
repair-both-modified.pl
```
