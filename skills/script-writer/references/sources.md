# Sources

Research base: 14 YouTube videos on short-form scriptwriting, scraped via Apify
(`streamers/youtube-scraper`) on 2026-07-28, filtered to the last ~6 months and to videos with
meaningful view counts, then ingested into NotebookLM and mined for the frameworks in this skill.

**NotebookLM notebook:** https://notebooklm.google.com/notebook/d0c88642-a607-465e-ab2a-27504ec9ece4

| Video | Creator | Published | Views |
|---|---|---|---|
| [My $75K YouTube Shorts System – Full Course In 19 Minutes](https://www.youtube.com/watch?v=srDpvEnGQg4) | E'Calm | 2026-03-14 | 783K |
| [The Ridiculous Engineering Of Short Form Content](https://www.youtube.com/watch?v=69Gw7aoWMMI) | Enrico Tartarotti | 2026-02-20 | 497K |
| [How I Write my Viral Script](https://www.youtube.com/watch?v=8oNrdEhksyE) | Abhimanyu Singh (Yash) | 2026-03-11 | 312K |
| [How I Actually Write Viral Scripts](https://www.youtube.com/watch?v=cX8c3R2LFd4) | Isaac | 2026-02-28 | 193K |
| [How to Write Viral Scripts Using AI (Works in Every Niche)](https://www.youtube.com/watch?v=Lyiwex_cj1k) | Aftab Khan | 2026-05-06 | 180K |
| [Write Viral Scripts For YouTube Videos](https://www.youtube.com/watch?v=FXGj-WVtxwM) | Tube Sensei | 2026-04-06 | 151K |
| [Say This in Your Videos, It'll Improve Your Storytelling by 10x](https://www.youtube.com/watch?v=pcnrzBwoVUk) | Kallaway | 2026-02-25 | 124K |
| [Scripting tips for beginners](https://www.youtube.com/watch?v=239GdtL6Whk) | Swati Dwivedi | 2026-03-28 | 114K |
| [These New Hooks are Dominating 2026](https://www.youtube.com/watch?v=5A6XVQUopYA) | vidIQ | 2026-03-18 | 47K |
| [The Hook Writing Formula Every Creator Needs!](https://www.youtube.com/watch?v=g935galOQ8Q) | Swati Dwivedi | 2026-05-29 | 36K |
| [(Full Course) Instagram Script Writing + Algorithm + Storytelling](https://www.youtube.com/watch?v=KnvlQIWrRDc) | Inside Q | 2026-01-03 | 30K |
| [How I Write Faceless YouTube Scripts That Get 100s Of Millions Of Views](https://www.youtube.com/watch?v=yxxVj5m-oAA) | Tim Danilov | 2026-03-20 | 19K |
| [How To Make YouTube Shorts Hooks That Go Viral Every Time](https://www.youtube.com/watch?v=Y3pAmxXNOU4) | moneyboymax | 2026-03-06 | 13K |
| [I Studied 1,000 TikTok Shop Hooks](https://www.youtube.com/watch?v=J3quLmejc7g) | Benjamin Jordan | 2026-02-05 | 9K |

Notes:
- View counts as at 2026-07-28.
- Inside Q's Instagram course is ~7 months old (just outside the 6-month window) — kept because it is the only Instagram-Reels-specific full course in the set and the source of the HRST framework.
- Two low-subscriber but high-signal sources (Tim Danilov, Benjamin Jordan) were included for platform-specific depth: faceless-narrative scripting and TikTok Shop hook data respectively.

## Refreshing this research

```bash
# 1. Re-scrape (Apify MCP): streamers/youtube-scraper
#    searchQueries: script writing / hook / retention terms
#    sortingOrder: views, dateFilter: year, then filter to last 6 months
# 2. Add the shortlisted URLs to a NotebookLM notebook (notebooklm-mcp: source_add)
# 3. Query the notebook for hooks / structures / platform differences / sentence craft
# 4. Update the reference files here with anything new
```
