# Instagram Friendship Graph

**See your Instagram friendships take shape.** Explore friends one, two, and three connections away, trace the paths between them, and uncover mutuals hiding in plain sight.

Here, a **friend** means a mutual follow: you follow someone and they follow you back. At later degrees, each connection likewise means both accounts follow each other. The project turns those observed connections into an Obsidian graph and a movable Canvas. The code and fictional example are safe for a public repository; your Instagram export, observations, and generated vault stay in ignored `local-data/`.

## Try it now

Requires Python 3.10+ and [Obsidian](https://obsidian.md/). No Python packages or Instagram login are needed.

```bash
python3 -m friendship_graph demo
```

In Obsidian, choose **Open folder as vault** and select `local-data/demo-vault`. Open `Friendship Rings.canvas` for movable, colored rings. Open `Home.md`, then use **Open local graph** and set depth to **3** for Obsidian's force-directed graph. The Canvas's circles are fixed on generation; you can drag cards in Obsidian, but regenerating the vault resets generated Canvas positions.

The demo has `you` at the center, Alex and Bea at degree 1, Casey at degree 2, and Drew at degree 3. Its usernames are fictional examples.

## Build your own

1. In Instagram, find **Accounts Center → Your information and permissions → Download your information**. Request your Instagram **followers and following** for **all time**, in **JSON** format. Meta places this feature in Accounts Center; labels may vary by account or app version. Keep the ZIP on your own machine.
2. Put the ZIP in `local-data/`, for example `local-data/instagram-export.zip`.
3. Run this command with your Instagram handle:

```bash
python3 -m friendship_graph build --account YOUR_HANDLE --export local-data/instagram-export.zip
```

The result is `local-data/vault/`. Open that folder in Obsidian. The importer reads only `followers*.json` and `following.json` in the export's `followers_and_following/` folder. It accepts the original ZIP or an extracted export directory. It does not upload anything or contact Instagram.

Your export tells us which accounts **you** follow and which follow **you**. Their intersection gives degree 1. It does **not** reveal who your friends follow, so it cannot establish degrees 2 and 3 on its own.

## Add second and third degree

Prepare a private collection task for your logged-in Grokbot:

```bash
python3 -m friendship_graph prepare-second-degree \
  --account YOUR_HANDLE \
  --export local-data/instagram-export.zip \
  --observations local-data/observations.json
```

It writes `local-data/second-degree-task.md` with up to ten reciprocal accounts that you followed most recently. **Recency is only a collection order, not a friendship score.** To select people yourself, put one mutual account per line in an ignored `local-data/targets.txt` file and add `--targets-file local-data/targets.txt`. The task stays local and private.

Have friends voluntarily share their own follower/following export, or collect only lists you can legitimately see. Ask Grokbot to prepare the new batch's JSON file using the private task and [the handoff](GROKBOT_HANDOFF.md). Each observed snapshot has this shape:

```json
[
  {
    "account": "alex",
    "followers": ["you", "bea", "casey"],
    "following": ["you", "bea", "casey"]
  }
]
```

Each list must describe the named account. Use empty arrays only when a list was fully observed and genuinely empty. Omit an account when a list was hidden. Captured subsets can contribute positive edges, but must be reported as incomplete. Then rebuild, repeating `--observations` for each batch:

```bash
python3 -m friendship_graph build \
  --account YOUR_HANDLE \
  --export local-data/instagram-export.zip \
  --observations local-data/observations.json \
  --observations local-data/second-degree-observations.json
```

An edge exists only when **both follow directions are observed**. Degree means the shortest path of reciprocal follow edges from you. It is a social network hop count, not a claim about real-life friendship or closeness. Unknown or incomplete lists do not prove that an edge is absent. The graph includes only nodes within three observed hops.

Instagram may show fewer usernames in a visible list than its profile badge count. A captured subset can still prove an edge when **both directions appear**, but its missing names cannot disprove one. Treat all degree counts from such snapshots as **observed lower bounds**, and record the collection limitation alongside your private data. Do not use an empty array to mean a list was inaccessible.

### Keep growing the graph

Run `prepare-second-degree` again with **every current observation file** to select unobserved first-degree accounts. Give each batch a new output filename such as `--output local-data/second-degree-batch-2.md`; the task will request a matching `.json` file. Never pass the original and a merged replacement for the same account together, because duplicate snapshots are rejected.

To select unobserved second-degree accounts for a third-degree batch:

```bash
python3 -m friendship_graph prepare-third-degree \
  --account YOUR_HANDLE \
  --export local-data/instagram-export.zip \
  --observations local-data/observations.json \
  --observations local-data/second-degree-observations.json \
  --observations local-data/third-degree-observations.json \
  --output local-data/third-degree-batch-2.md
```

Use the latest merged observation file for each account. Add `--exclude-file local-data/inaccessible-accounts.txt` if you have a file with one inaccessible username per line. The third-degree batch favors second-degree accounts with more observed links into your first-degree ring; this is a collection heuristic, not a measure of closeness. Keep all task and data files in ignored `local-data/`.

If `observations.json` also contains your own account, that snapshot is ignored when it exactly matches your Meta export. A mismatch stops the build so the two sources are not silently mixed.

Generated person notes have `degree-1`, `degree-2`, or `degree-3` tags, which you can use for graph groups and searches. The `People/` notes, `Home.md`, and Canvas are generated files and may be replaced on rebuild; keep personal annotations in separate notes in the same vault. The generator refuses to overwrite a note that it did not create.

## Privacy

- Keep `local-data/` private. It includes other people's handles, even when the names are publicly visible on Instagram.
- Do not paste credentials, cookies, session files, or raw exports into GitHub issues, commits, or Grokbot prompts.
- Before publishing any change, run `git status --short` and inspect staged files with `git diff --cached --name-only`.
- If you choose a custom `--output` path, keep it outside tracked files. The default location is already ignored.

## How it works

The importer takes follower and following snapshots and records directed follow facts. A reciprocal pair becomes one undirected friendship edge. Breadth-first search assigns degrees 0–3 from your account. It writes linked Markdown notes for Obsidian's graph and a standards-based `.canvas` file with deterministic positions and colors. Rebuilding from updated data updates the view.

Sources: [Meta on Download Your Information in Accounts Center](https://about.fb.com/news/2023/10/manage-your-information-across-apps/), [Obsidian Graph view](https://obsidian.md/help/plugins/graph), [Obsidian Canvas](https://obsidian.md/help/plugins/canvas), [JSON Canvas specification](https://jsoncanvas.org/spec/1.0/).
