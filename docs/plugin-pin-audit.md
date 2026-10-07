# Default plugin remote audit

Read-only exact-object fetches and tracking-ref comparisons completed 2026-10-07. The tested commits below were fetchable from each canonical repository. “Newer” means the advertised tracking ref had advanced beyond the tested commit at audit time; no pin was promoted.

| Plugin ID | Canonical repository | Tracking ref | Tested revision | Fetchable | Newer candidate |
|---|---|---|---|---|---|
| `com.omastorm.radar` | https://github.com/wesleygrimes/omastorm.git | `refs/heads/main` | `aaa297a6b4930a721d1e5cad1243d7886ceb096e` | yes | yes |
| `crmne.active-window` | https://github.com/crmne/omarchy-active-window.git | `refs/heads/main` | `ca8fdab2fed809c7e9368d1a3bfd310f3896b4cc` | yes | yes |
| `djjeane.docker-monitor` | https://github.com/djjeane/omarchy-docker-plugin.git | `refs/heads/master` | `81c95ec532b255d5d2bc98f6ff42c936608e9ead` | yes | no |
| `dki.hijri-calendar` | https://github.com/korex-f/omarchy-hijri-calendar.git | `refs/heads/master` | `e02fbfaf2eb9ad741ad9afed68f6cbedb1599cab` | yes | no |
| `fkcodes.key-promoter` | https://github.com/ForrestKnight/omarchy-key-promoter.git | `refs/heads/main` | `ecbfcc5c291bce1506f694d2d66b1ebffba1a5c9` | yes | no |
| `io.github.dki.tugboat` | https://github.com/korex-f/tugboat.git | `refs/heads/main` | `73b2071eb14442613bf32abd77424a5a0c4263b9` | yes | no |
| `io.github.huligabuliga.omasticky` | https://github.com/huligabuliga/Omasticky.git | `refs/heads/master` | `b6a36934d970e79ea80119748fd0713cf03e46b0` | yes | no |
| `io.github.jondkinney.omapop` | https://github.com/jondkinney/omapop.git | `refs/heads/main` | `7880a508af6a511dd741ac3074e8d7d8cf1367d7` | yes | yes |
| `io.github.mtolhuys.fathom` | https://github.com/mtolhuys/fathom.git | `refs/heads/main` | `0135dae264268d7457aa2d2e18716b9cd813e6c8` | yes | yes |
| `local.prayer-times` | https://github.com/husamemadH/omarchy-quattro-prayer-times.git | `refs/heads/master` | `03306f14f3a8d37425bb42c097fa1a4b0eadd2eb` | yes | yes |
| `nixfred.burnbar` | https://github.com/nixfred/burnbar.git | `refs/heads/master` | `2b827cfa9007884fe178034ac645bc277f139636` | yes | yes |
| `omaplug` | https://github.com/fross100/omaplug | `refs/heads/main` | `6d6391fd3bc9e0738d0b52477f28f3e5b3533e5b` | yes | yes |
| `robzolkos.github` | https://github.com/robzolkos/omarchy-github.git | `refs/heads/main` | `c6e6633b2be7bf55c35b51b1bd7702ba24e64624` | yes | yes |
| `shell.settings` | https://github.com/AyushKr2003/shell-settings.git | `refs/heads/main` | `2d6cdf7e9eb741f83dea17077f18b0df287db28c` | yes | no |
| `slcode777.omaconv` | https://github.com/SLcode777/omaconv.git | `refs/heads/master` | `1cca7b85b8f91b7d1e3c0efb236e903a1ef156f2` | yes | no |
| `ssandys.galley` | https://github.com/ssandys/galley.git | `refs/heads/master` | `ffd78a11ec0b70e32dc98b2a5fcc438ef6dca43f` | yes | yes |
| `tech.greyforge.reprieve` | https://github.com/GreyforgeLabs/reprieve.git | `refs/heads/main` | `38c6292e7f22e554935c36f6597b8a1bac5e146f` | yes | yes |
| `tornikegomareli.spaces` | https://github.com/tornikegomareli/omarchy-spaces.git | `refs/heads/main` | `f8306d763c7b3c89d24172edb0e68fb6dacb68a9` | yes | yes |

Tugboat `73b2071eb14442613bf32abd77424a5a0c4263b9` was fetchable and remained the advertised `main` tip; its former local ahead display was stale tracking metadata. Theme Picker is excluded and therefore not among selected defaults; its historical local revision is not remotely fetchable from its recorded URL.
