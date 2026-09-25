# Task for a Grokbot with access to my Instagram account

Copy the text below to Grokbot. Replace `YOUR_HANDLE` before sending. Do not include your password or session cookies.

> I am building a **local, private Obsidian friendship graph** for my Instagram account `YOUR_HANDLE`. Please use my logged-in Instagram session only to help me get data I can access. Do not publish, post, message anyone, change my account settings, or upload the data to GitHub.
>
> **First, get my own data.** In Instagram/Meta Accounts Center, request or retrieve my Download Your Information export for **followers and following**, covering **all time**, in **JSON** format. Give me the original ZIP privately. If the export is not ready, tell me the exact screen/status and what I need to do next. Do not send the ZIP to a public repository or paste its contents in chat.
>
> **Optional expansion:** For a small set of accounts I name, record their complete follower and following lists only when those lists are visible to my account or the account owner has shared them with me. Do not bypass access controls, use another person's credentials, or infer missing relationships. If either list is incomplete, inaccessible, or uncertain, omit that account and report why.
>
> If you have complete snapshots, create a UTF-8 JSON file named `observations.json`. It must be an array of objects with exactly these keys: `account`, `followers`, `following`. Values are Instagram usernames without `@`; each of the two lists belongs to that `account`. Include no emails, phone numbers, DMs, profile descriptions, or timestamps. Deduplicate usernames. Give me this file privately, not a chat dump and not a GitHub upload.
>
> Report the number of accounts included and the accounts omitted because their lists were unavailable or incomplete. Keep all raw data local/private.

Place the files in this repo's ignored `local-data/` folder and run the commands in [README.md](README.md). Start with your own export; that alone gives a useful first-degree graph.

## Next collection task for this graph

If your own export has already been processed and `observations.json` repeats only your account, it adds no second or third degree nodes. For expansion, send Grokbot this follow-up after replacing `YOUR_HANDLE`:

> My own Instagram export is already processed. Please do **not** repeat `YOUR_HANDLE` in `observations.json`. To expand the graph, start with up to 10 of my reciprocal-follow accounts that I name or approve. For each other account, record its **complete** `followers` and **complete** `following` username lists only if both are available to my logged-in account or shared by that account owner. Put one object per account in `observations.json` with exactly `account`, `followers`, and `following`. If a list is hidden, truncated, or uncertain, omit that account and report it. Return the JSON privately. Do not upload it to GitHub.

The generator will use reciprocal follow evidence from those snapshots to place reachable accounts at two or three hops. It cannot infer missing connections from your own export.
