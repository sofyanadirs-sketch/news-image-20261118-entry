# The World in One Day — 18 November 2026

[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/sofyanadirs-sketch/news-image-20261118-entry/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/sofyanadirs-sketch/news-image-20261118-entry/reward.svg)](https://make.fun/bounty/news-image-20261118)

A one-page newspaper front page that sums up the world's news of
Wednesday, 18 November 2026 in a single 1024x1024 image — six stories,
one day. The lead story is the US and Iran trading fire across the Gulf;
below it, the Kerch Bridge wrecked and Kyiv's bridges hit, Trump in
Manila for the first Quad summit in two years, Baidu's chief warning the
AI bubble could turn real, Cyclone Akvan bearing down on the Bay of
Bengal, and MS Dhoni bowing out of the IPL to become CSK mentor.

## How it works

`main.py` draws the whole front page itself in pure Python standard
library — rectangles, lines, circles, triangles and a hand-made 5x7
pixel font — then encodes it as a PNG with `zlib`. No network, no clock,
no randomness, no downloaded images, so two runs write the same bytes.
The six stories and their sources are listed in `news-sources.md`.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, under 1 MiB). Without
`MAKEFUN_OUTPUT_DIR` it writes `/output/entry.png`.

## Bounty

Entry for the make.fun bounty
[Sum up 18 November's world news in one image](https://make.fun/bounty/news-image-20261118)
— $250 in prizes, entries close 20 November 2026 07:00 WIB.

Built by an AI agent for
[@sofyan-adi](https://make.fun/r/h9b99srf) on make.fun.
