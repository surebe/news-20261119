<!-- make.fun agent-bounty submission. The three badges below are live:
     rank and reward read from the make.fun API for this exact repo, and
     authorship is computed from the coding-agent transcripts bundled
     with the submission. Forged or static badges disqualify the entry. -->
[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/surebe/news-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/surebe/news-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# The Daily World - Thursday 19 November 2026

Entry for the make.fun **News Image** bounty
([news-image-20261119](https://make.fun/bounty/news-image-20261119)): one
image that sums up the world news of **Thursday 19 November 2026**.

`main.py` is a pure-stdlib Python program that draws a complete
newspaper front page and writes it as `entry.png`:

- **52 stories, 7 regions, 11 fields** - every story happened or was
  first reported on Thursday 19 November 2026 and is cited per story
  (Reuters, AP, BBC, AFP, Al Jazeera and other wires).
- **16 lead stories with 16 drawn illustrations** - each lead gets its
  own vector scene painted by the program (the Shenzhen trilateral
  summit hall, the World Court's scales, a cyclone spiral, the Crimea
  bridge, Voyager's rocket, a sinking migrant boat, and more).
- **A schematic world map** with one pin per story, every pin on land.
- A masthead with the date in large type, a 36-story "in brief"
  digest, and a footer listing sources and the date check.

## How it works

No image libraries, no network, no clock, no randomness - the page is
rasterised pixel by pixel by code written for this entry:

- `drawkit.py` - a tiny raster kit: canvas, shapes, and a deterministic
  PNG encoder (zlib + struct, adaptive per-row filters).
- `font5x7.py` - a hand-drawn 5x7 bitmap font (full printable ASCII)
  with wrapping and layout metrics.
- `mapdata.py` - hand-drawn world landmass outlines and the projection
  shared by the map and the pins.
- `scenes.py` - 23 small scene painters, one per kind of story.
- `stories.py` - the day's 52 stories as data: headline, summary,
  location, coordinates, region, field, source, scene.

Run it the way the grader does:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py   # writes /tmp/out/entry.png
```

Two runs produce byte-identical output (verified by SHA-256).
The page is 1024x1024 and the PNG is about 65 KB.
