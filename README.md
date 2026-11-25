# News Image — 25 November 2026

[![Competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/machero007/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/machero007/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

**Sum up 25 November's world news in one image** — an entry for the
[make.fun news-image-20261125 bounty](https://make.fun/bounty/news-image-20261125).

One dense 1024×1024 image carrying the whole day: Wednesday, 25 November
2026. Four headline panels — the Houthi strike on Saudi Arabia's Ras Tanura
refinery and Riyadh financial district, China's Shenzhou-24 flight carrying
the first foreign astronaut (Pakistan's Muhammad Zeeshan Ali) to Tiangong,
the US jury convicting Huawei on 10 of 12 counts, and Bangladesh raising its
garment minimum wage 36% to 17,000 taka — plus 19 more verified stories, a
UTC wire strip, and a sources footer. Every story was first reported or
confirmed on 25 November 2026 (UTC) by Reuters, AP, BBC, AFP or CNN, and
each pictogram is drawn from scratch with PIL — no external images.

## Run it

```bash
python3 build_image.py   # regenerates entry.png (deterministic)
python3 main.py          # copies entry.png to /output/entry.png
```

`build_image.py` uses Python 3.13 standard library + Pillow only, with no
network access and no timestamps in the output, so re-running it produces a
byte-identical PNG. `main.py` is standard library only.

## License

MIT — see [LICENSE](LICENSE).

---

Built for [make.fun](https://make.fun/?ref=nnnrkexm).
