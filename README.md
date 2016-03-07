# AutoSteamGifts
A Python script to automatically enter every giveaway that you can afford on SteamGifts.com

**Format:**

The format is pretty straightforward, the program only needs your cookie in order to have access to your SteamGifts session.
Optionally, you can insert the SteamGifts page number for paging purposes.

    Usage: ./steamgifts.py <Cookie (first execution only)> [<starting page (default=1)>]
    
In order to obtain your cookie, you can press CTRL+SHIFT+J while on SteamGifts.com (CTRL+SHIFT+K on Firefox) and type **document.cookie**. Then use the whole string (quotes included) as the argument.
**You only need need to do this once because AutoSteamGifts will remember your cookie (if valid).**
