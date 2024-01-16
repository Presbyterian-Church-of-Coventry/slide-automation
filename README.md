# Slide Automation

I should've written this ages ago, it would have saved at least 50 tedioius hours! But, as they say, better late than never.

At this point, this whole system is tailored only for this church (PCC). If anyone ever wants to attempt to reuse this code, you'll need to replace and resize your `logo.jpg` and rewrite a good deal of the custom bulletin fetching.

**Disclaimer:** The entire fiddly mess that is `write_verses()` is liable to combust at the slightest modification, and I've spent hours tweaking it to adhere as closely as possible to the formatting guidelines I've applied by hand for years. However, I'm sure there is some odd edge case in ESV formatting I've neglected to write a routine for, so feel free to attempt a fix and a PR would be welcomed if you have any improvements.

### Usage

To use this project in it's current form, you'll need to check it out with

```
git clone https://github.com/Presbyterian-Church-of-Coventry/slide-automation.git
```

Assuming you have a recent version of Python installed, you'll then need to install this project's dependecies: 

```
pip3 install -r requirements.txt
```

Before running, you'll need to rename `.env_example` to `.env` and fill in the needed variables in order to pull all the needed information and save slides in the correct places.

You should now be good to go! Run

```
python3 main.py
```

And enter the date you wish to generate slides for in YYYY-MM-DD format when prompted.
If the bulletin exists on the church website, it'll generate slides for all the linked verse and hymns in your configured slide directory!

### To-Do:

- [ ] Allow manual intervention for things like hymn inserts that don't have an absolute source of truth
- [ ] Make this into a flexible API called from the website to make it more accessible for future A/V staff
